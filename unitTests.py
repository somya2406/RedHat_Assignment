import unittest
import tempfile
import os
import pandas as pd
from Services.service import Service  

class TestService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_csv_content = """Date,Product,Quantity,Price
2025-01-01,Apple,"10",1.2
2025-01-02,Banana,5,0.8
2025-01-03,APPLE,15,1.3
2025-01-04,Orange,8,1.5
2025-01-05,Banana,12,0.7
2025-01-06,DAAD,1,2.0
2025-01-07,ABVBA,4,1.1
2025-01-08,,9,1.0
2025-01-09,ADDA,,1.3
2025-01-10,,6,1.2
2025-01-11,VADAV,2,
2025-01-12,Avocado,7,1.4
2025-01-13,Banana,0,0.0
2025-01-14,apple pie,10,1.1
2025-01-15,banana split,20,1.6
2025-01-16,NAVAN,3,1.3
2025-01-17,ABABA,11,1.9
2025-01-18,Apple,99,10.5
2025-01-19,BaNANa,13,0.9
2025-01-20,DEED,14,2.1
2025-01-21,,,
2025-01-22,Orange,not_a_number,0.8
2025-01-23,Apple,23,one_point_two
"""
        cls.temp_csv_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv')
        cls.temp_csv_file.write(cls.test_csv_content)
        cls.temp_csv_file.close()
        cls.service = Service(cls.temp_csv_file.name)

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.temp_csv_file.name)

    def test_display_rows_correctly(self):
        self.service.display_first_n_rows(2)

    def test_filter_for_contains(self):
        
        rss = self.service.filter_rows_based_on_condition("Product", "contains Apple")
        self.assertFalse(rss.empty)
        self.assertTrue(rss['Product'].astype(str).str.upper().str.contains("APPLE").any())

      
        rsn = self.service.filter_rows_based_on_condition("Quantity", "contains 10")
        self.assertFalse(rsn.empty)
        self.assertTrue(rsn['Quantity'].astype(str).str.contains("10", case=False).any())

    def test_filter_for_numeric(self):
        rs = self.service.filter_rows_based_on_condition("Quantity", "> 10")
        self.assertIn(12, rs["Quantity"].dropna().values)

    def test_invalid_filter_column(self):
        rs = self.service.filter_rows_based_on_condition("InvalidCol", "> 10")
        self.assertTrue(rs.empty)

    def test_sort_rows_by_column(self):
        rs = self.service.sort_rows_by_column("Quantity")
        self.assertTrue(rs["Quantity"].dropna().is_monotonic_increasing)

    def test_aggregate_sum_in_column(self):
        total_rs = self.service.aggregate_column_data("Quantity", "sum")
        expected_vals = [10, 5, 15, 8, 12, 1, 4, 9, 6, 2, 7, 0, 10, 20, 3, 11, 99, 13, 14, 23]  
        self.assertAlmostEqual(total_rs, sum(expected_vals))  

    def test_aggregate_average_in_column(self):
        avg = self.service.aggregate_column_data("Quantity", "average")
        expected_vals = [10, 5, 15, 8, 12, 1, 4, 9, 6, 2, 7, 0, 10, 20, 3, 11, 99, 13, 14, 23]
        self.assertAlmostEqual(avg, sum(expected_vals) / len(expected_vals))

    def test_invalid_aggregate_column(self):
        self.assertIsNone(self.service.aggregate_column_data("Product", "sum"))

    def test_invalid_aggregate_operation(self):
          self.assertIsNone(self.service.aggregate_column_data("Quantity", "median"))

    def test_count_valid_palindromes(self):
        self.assertEqual(self.service.check_valid_palindromes(), 6)  

    def test_write_to_csv(self):
        temp_file_check = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        temp_file_check.close()
        df = self.service.filter_rows_based_on_condition("Product", "contains Apple")
        self.service.write_in_csv_file(df, temp_file_check.name)
        self.assertTrue(os.path.exists(temp_file_check.name))
        file_content = pd.read_csv(temp_file_check.name)
        self.assertFalse(file_content.empty)
        os.unlink(temp_file_check.name)


if __name__ == "__main__":
    unittest.main()

