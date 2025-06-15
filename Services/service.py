import pandas as pd
import os
import re
from enum import Enum

allowedPalindrome = set("ADVBN")

class Service:

    def __init__(self, curr_file_path):
        if not os.path.exists(curr_file_path):
            raise FileNotFoundError(f"CSV file with the given path {curr_file_path} does not exist")
        df = pd.read_csv(curr_file_path)

        print("####### Validating CSV file and cleaning data #########\n")

        for col_n in df.select_dtypes(include='object').columns:
            df[col_n] = df[col_n].apply(lambda x: x.strip() if isinstance(x, str) else x)

        df.replace('', pd.NA, inplace=True)

        empty_row_n = df[df.isna().all(axis=1)]

        if empty_row_n.empty==False:
            print(f"Found {len(empty_row_n)} empty rows and these rows will be dropped.")
        df = df.dropna(how='all')
                
        for col in df.select_dtypes(include='object').columns:
            num_coercion = pd.to_numeric(df[col], errors='coerce')
            non_na_ratio = num_coercion.notna().sum() / len(df)
            if non_na_ratio > 0.7:  
                df[col] = num_coercion

        for col_n, cnt_of_Nan in df.isna().sum().items():
            if cnt_of_Nan > 0:
                print(f"Column '{col_n}' has {cnt_of_Nan} missing/invalid value(s).")
                
        self.dataFrame = df
        print("CSV file validated and cleaned successfully.\n")
    
    def write_in_csv_file(self, data, nfile_path)-> bool:

        file_exists = os.path.exists(nfile_path)
        data.to_csv(nfile_path, index=False)

        if file_exists:
            print(f"File '{nfile_path}' already existed and has been overwritten.")
            return True
        elif not file_exists:
            print(f"File '{nfile_path}' has been created successfully with the data.")
            return True
        else:
            print(f"Error while writing to file '{nfile_path}'")
            return False

            

    def display_first_n_rows(self, n=3)-> None:
        if not self.is_data_loaded():
            return None
        
        if n >= len(self.dataFrame):
            print(f"Displaying all rows since requested no of rows  {n} is greater than available number of rows{len(self.dataFrame)}\n")
            print(self.dataFrame.to_string(index=False))
            return None
        else:
            print(f"Displaying first {n} rows:\n")
            print(self.dataFrame.head(n).to_string(index=False))
            return None

    def filter_rows_based_on_condition(self, col_n, filter_condition,path_for_file =None)-> pd.DataFrame:
        
        if not self.is_data_loaded():
            return pd.DataFrame()
        try:
            col_n = self.get_valid_column_name(col_n)
            if not col_n:
                return pd.DataFrame()                  

            if self.dataFrame[col_n].isna().any():
                missing_values_cnt = self.dataFrame[col_n].isna().sum()
                print(f"WARNING:: Column '{col_n}' has {missing_values_cnt} missing values. These will be ignored.\n")
            filtered_data = pd.DataFrame() 
            
            if FilterOperation.CONTAINS.value in filter_condition.upper():
                substr_match = re.match(rf"^{FilterOperation.CONTAINS.value}\s*(\S.*)", filter_condition, re.IGNORECASE)
                if substr_match:
                    substring = substr_match.group(1).strip()
                    if substring:
                        filtered_data = self.dataFrame[self.dataFrame[col_n].astype(str).str.contains(substring, case=False, na=False)]
                    else:
                        print("Empty substring provided after contains.")
                        return pd.DataFrame()
  
            elif match := re.match(r"([><=!]=?|==)\s*(\d+(?:\.\d+)?)", filter_condition.replace(" ", "")):
                op = match.group(1)
                value = match.group(2)
                if not pd.api.types.is_numeric_dtype(self.dataFrame[col_n]):
                    print(f"Column '{col_n}' is not numeric. Cannot apply condition '{filter_condition}'.")
                    return pd.DataFrame()

                else:
                    query = f"{col_n} {op} {value}"
                    filtered_data = self.dataFrame.query(query)
            else:
                print(f"Invalid filter condition: '{filter_condition}'. Use 'contains <substring>' or '<op> <value>' format.")
                return pd.DataFrame()

            if filtered_data.empty:
                print("No rows matching the given condition.")
                return pd.DataFrame()
            
            print(f"{len(filtered_data)} rows matched: {col_n} {filter_condition}")
            print(filtered_data.to_string(index=False))
            if path_for_file:
                self.write_in_csv_file(filtered_data,path_for_file,)

            return filtered_data

        except Exception as e:
            print(f"Error filtering the rows: {e}")
            return pd.DataFrame()

    def sort_rows_by_column(self, col_n, path_for_file=None,ascending=True)-> pd.DataFrame:

        if not self.is_data_loaded():
            return pd.DataFrame()
        col_n = self.get_valid_column_name(col_n)
        if not col_n:
            return pd.DataFrame()   
        
        sorted_data = self.dataFrame.sort_values(by=col_n, ascending=ascending)
        print(f"Data sorted by '{col_n}' ({'ascending' if ascending else 'descending'})")
        print(sorted_data.to_string(index=False))
        if path_for_file:
            self.write_in_csv_file(sorted_data, path_for_file)
        return sorted_data        


    def aggregate_column_data(self, col_n, op)->None | float:

        if not self.is_data_loaded():
            return None        
        col_n = self.get_valid_column_name(col_n)
        if not col_n:
            return None   
        if not pd.api.types.is_numeric_dtype(self.dataFrame[col_n]):
                print(f"Column '{col_n}' must have numeric values for operation '{op}'.")
                return None
 
        if op.lower().strip() == "min":
            return self.dataFrame[col_n].min()
        elif op.lower().strip() == "max":
            return self.dataFrame[col_n].max()
        elif op.lower().strip() == "sum":
            return self.dataFrame[col_n].sum()
        elif op.lower().strip() == "average":
            return self.dataFrame[col_n].mean()
        else:
            print("Invalid operation: suported operations are sum, average, min, max.")
            return None


    def check_valid_palindromes(self)-> int | None:
  
        if not self.is_data_loaded():
            return None
        valid_pl_list = []
        for col_n in self.dataFrame.columns:
            for val in self.dataFrame[col_n].dropna().astype(str):
                val_upper = val.strip().upper()
                if set(val_upper).issubset(allowedPalindrome):
                    if self.is_valid_palindrome(val_upper):
                        valid_pl_list.append(val)
        
        len_pl_list = len(valid_pl_list)
        if valid_pl_list:
            print(f"Total valid palindromes using values (A, D, V, B, N) are : {len_pl_list}")
            print("Valid palindromes using only given values (A, D, V, B, N) are:")
            for p in valid_pl_list:
                print(p)
        else:
            print("No valid palindromes found using only A, D, V, B, N.")
        return len_pl_list
    
    def get_valid_column_name(self, col_n: str) -> str | None:

        if not self.is_data_loaded():
            return None
        normalized_cols = {c.strip().upper(): c for c in self.dataFrame.columns}
        col_key = col_n.strip().upper()
        if col_key not in normalized_cols:
            print(f"WARNING:: Column '{col_n}' not found in the CSV.")
            return None
        return normalized_cols[col_key]

    def is_valid_palindrome(self,val)-> bool:
        val = val.strip().upper()
        return set(val).issubset(allowedPalindrome) and val == val[::-1]
    
    def is_data_loaded(self) -> bool:
        if not hasattr(self, 'dataFrame') or self.dataFrame.empty:
            print("No data loaded in the service.")
            return False
        return True

            

class FilterOperation(Enum):
    CONTAINS = "CONTAINS"

    


