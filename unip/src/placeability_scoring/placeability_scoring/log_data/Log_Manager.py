import pandas as pd
import os


class Log_Manager():
    """Logmaster is used to track logs and save them over multiple trials in files
    Its designed to also work with new logs and adds it to the dataframe
    The add function is mainly used for time measurements to add times on indices in case of loops.
    """
    def __init__(self, path):
        self.log_path = path # ends with .csv or .parquet
        self.log = {}

    def add(self, index, value):
        if index in self.log:
            self.log[index] += value
        else:
            self.log[index] = value
            
        print(f"Execution time for:     {index}         Total: {self.log[index]:.4f}s,     Added {value:.4f}s")
            
    def save(self):
        # Convert current timing dict to DataFrame row
        df_new = pd.DataFrame([self.log])
        # If file exists, append row
        if os.path.exists(self.log_path):
            df_existing = pd.read_csv(self.log_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        # Save updated log
        df_combined.to_csv(self.log_path, index=False)



if __name__ == "__main__":
    log_path = "timing_log.csv"
    logmaster_test = Log_Manager(path = log_path)
    
    logmaster_test.log = timings = {
        "grasp_time": 0.512,
        "place_time": 0.422,
        "collision_check": 0.103,
    }
    logmaster_test.add(index="test2", value=0.2)
    logmaster_test.add(index="test3", value=0.33)
    logmaster_test.add(index="test2", value=0.2)
    
    logmaster_test.save()