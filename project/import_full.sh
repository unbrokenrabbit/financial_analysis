#!/bin/bash

PYTHON=python3
SCRIPT=analyze.py

python3 analyze.py import test_files/checking_bills.csv checking_bills
python3 analyze.py import test_files/checking_spending.csv checking_spending
python3 analyze.py import test_files/credit_bills.csv credit_bills
python3 analyze.py import test_files/credit_spending.csv credit_spending
