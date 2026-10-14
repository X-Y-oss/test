import argparse
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision import transforms as pth_transforms

ROOT = Path("/workspace/experimental/FeelAnyForce")

sys.path.insert(0, str(ROOT))

from composed_model import ComposedModel
from args import get_parser


CKPT_PATH = ROOT / "ckpt/checkpoint_v1.pth.tar"

PREGRASP_PATH = (
    ROOT / "tacex_samples/pregrasp_right_tactile.npy"
)

POST_CLOSE_PATH = (
    ROOT / "tacex_samples/post_close_right_tactile.npy"
)

POST_GRASP_SETTLED_PATH = (
    ROOT / "tacex_samples/post_grasp_settled_right_tactile.npy"
)

CONTACT_PATHS = {
    "POST_CLOSE": ROOT / "tacex_samples/post_close_right_tactile.npy",
    "PRE_RELEASE": ROOT / "tacex_samples/pre_release_right_tactile.npy",
    "POST_GRASP_SETTLED": ROOT / "tacex_samples/post_grasp_settled_right_tactile.npy",
}


def load_tacex_rgb(path):
    img = np.load(path)

    print(f"{path.name}")
    print(" shape:", img.shape)
    print(" dtype:", img.dtype)
    print(
        " min/max:",
        float(img.min()),
        float(img.max()),
    )

    if img.shape != (240, 320, 3):
        raise RuntimeError(
            f"Unexpected image shape: {img.shape}"
        )

    # TacEx gives RGB float in [0,1].
    img_u8 = np.clip(
        img * 255.0,
        0,
        255,
    ).astype(np.uint8)

    return img_u8


print("Loading checkpoint...")
ckpt = torch.load(
    CKPT_PATH,
    map_location="cpu",
    weights_only=False,
)

parser = get_parser()

if "config" in ckpt:
    config = argparse.Namespace(**ckpt["config"])
    args = parser.parse_args([], namespace=config)
else:
    args = parser.parse_args([])

print("Model config:")
print(" tactile_model:", args.tactile_model)
print(" crop_size:", args.crop_size)
print(" num_labels:", args.num_labels)
print(" forward:", args.forward)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("device:", device)

print("Creating FeelAnyForce model...")
model = ComposedModel(args)

model.load_state_dict(
    ckpt["state_dict"]
)

model.eval()
model.to(device)

print("model loaded")

# Official dataset statistics for:
# TacForce_train_set.csv / nobg
mean_rgb = [
    0.36541664600372314,
    0.3716222047805786,
    0.36927229166030884,
]

std_rgb = [
    0.21197719871997833,
    0.2151239663362503,
    0.21367691457271576,
]

transform_rgb = pth_transforms.Compose([
    pth_transforms.Pad([0, 40, 0, 40]),
    pth_transforms.Resize(args.crop_size),
    pth_transforms.ToTensor(),
    pth_transforms.Normalize(
        mean_rgb,
        std_rgb,
    ),
])


background = load_tacex_rgb(
    PREGRASP_PATH
)

results = {}

for name, contact_path in CONTACT_PATHS.items():
    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    contact = load_tacex_rgb(
        contact_path
    )

    processed = (
        contact.astype(np.int16)
        - background.astype(np.int16)
        + 127
    )

    processed = np.clip(
        processed,
        0,
        255,
    ).astype(np.uint8)

    print(
        "processed min/max/mean:",
        processed.min(),
        processed.max(),
        processed.mean(),
    )

    image = Image.fromarray(processed)

    image_tensor = (
        transform_rgb(image)
        .unsqueeze(0)
        .to(device)
    )

    with torch.no_grad():
        intermediate_output = (
            model.tactile_backbone(
                image_tensor
            )
        )

        output = model.regressor(
            intermediate_output
        )

    force = output.squeeze(0).cpu().numpy()

    fx = float(force[0])
    fy = float(force[1])
    fz = float(force[2])

    fmag = float(
        np.sqrt(
            fx**2 +
            fy**2 +
            fz**2
        )
    )

    results[name] = {
        "Fx": fx,
        "Fy": fy,
        "Fz": fz,
        "Fmag": fmag,
    }

    print(f"Fx:  {fx:.6f} N")
    print(f"Fy:  {fy:.6f} N")
    print(f"Fz:  {fz:.6f} N")
    print(f"|F|: {fmag:.6f} N")

fx = float(force[0])
fy = float(force[1])
fz = float(force[2])

fmag = float(
    np.sqrt(
        fx**2 +
        fy**2 +
        fz**2
    )
)

a = results["POST_CLOSE"]
b = results["PRE_RELEASE"]

print()
print("=" * 60)
print("COMPARISON")
print("=" * 60)

print(
    f"delta Fx:  "
    f"{b['Fx'] - a['Fx']:+.6f} N"
)

print(
    f"delta Fy:  "
    f"{b['Fy'] - a['Fy']:+.6f} N"
)

print(
    f"delta Fz:  "
    f"{b['Fz'] - a['Fz']:+.6f} N"
)

print(
    f"delta |F|: "
    f"{b['Fmag'] - a['Fmag']:+.6f} N"
)
