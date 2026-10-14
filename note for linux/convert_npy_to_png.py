from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path("/workspace/experimental/FeelAnyForce/tacex_samples")
OUT = ROOT / "png"
OUT.mkdir(exist_ok=True)


for path in sorted(ROOT.glob("*.npy")):
    arr = np.load(path)

    print(
        f"{path.name}: "
        f"shape={arr.shape}, "
        f"dtype={arr.dtype}, "
        f"min={arr.min():.4f}, "
        f"max={arr.max():.4f}"
    )

    # ---------------------------------------------------------
    # TacEx tactile RGB: float [0, 1] -> uint8 RGB
    # ---------------------------------------------------------
    if "tactile" in path.stem:
        img = np.asarray(arr)

        if img.ndim == 4 and img.shape[0] == 1:
            img = img[0]

        if img.ndim != 3 or img.shape[-1] != 3:
            print(f"  SKIP unexpected tactile shape: {img.shape}")
            continue

        img_u8 = np.clip(
            img * 255.0,
            0,
            255,
        ).astype(np.uint8)

        out_path = OUT / f"{path.stem}.png"
        Image.fromarray(img_u8, mode="RGB").save(out_path)

        print(f"  -> {out_path}")

    # ---------------------------------------------------------
    # TacEx height map: normalize for visualization
    # ---------------------------------------------------------
    elif "height" in path.stem:
        h = np.asarray(arr, dtype=np.float32)

        if h.ndim == 3 and h.shape[0] == 1:
            h = h[0]

        h_min = float(h.min())
        h_max = float(h.max())

        if h_max > h_min:
            h_norm = (
                (h - h_min)
                / (h_max - h_min)
            )
        else:
            h_norm = np.zeros_like(h)

        h_u8 = np.clip(
            h_norm * 255.0,
            0,
            255,
        ).astype(np.uint8)

        out_path = OUT / f"{path.stem}.png"
        Image.fromarray(h_u8, mode="L").save(out_path)

        print(f"  -> {out_path}")

print("\nDONE")
print("PNG directory:", OUT)
