from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

FILE_NAME = "transactions.xlsx"

def init_excel():
    if not os.path.exists(FILE_NAME):
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl') as writer:
            df_fraud = pd.DataFrame(columns=["Name", "ID", "Amount", "Fraud %"])
            df_safe = pd.DataFrame(columns=["Name", "ID", "Amount"])
            
            df_fraud.to_excel(writer, sheet_name="Fraud", index=False)
            df_safe.to_excel(writer, sheet_name="Safe", index=False)

# Backend logic
def backend_check(amount):
    if amount > 50000:
        return 80
    elif amount > 20000:
        return 50
    else:
        return 10

# Final decision (combine frontend + backend)
def final_fraud_score(frontend_score, backend_score):
    final_score = (frontend_score * 0.6) + (backend_score * 0.4)
    
    if final_score > 60:
        return True, int(final_score)
    else:
        return False, int(final_score)

def save_to_excel(name, user_id, amount, fraud, percent):
    with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        
        if fraud:
            df = pd.read_excel(FILE_NAME, sheet_name="Fraud")
            new_row = pd.DataFrame([[name, user_id, amount, percent]],
                                   columns=["Name", "ID", "Amount", "Fraud %"])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(writer, sheet_name="Fraud", index=False)
        else:
            df = pd.read_excel(FILE_NAME, sheet_name="Safe")
            new_row = pd.DataFrame([[name, user_id, amount]],
                                   columns=["Name", "ID", "Amount"])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(writer, sheet_name="Safe", index=False)

@app.route('/check', methods=['POST'])
def check_transaction():
    data = request.json

    name = data.get("name")
    user_id = data.get("id")
    amount = float(data.get("amount"))
    frontend_score = float(data.get("frontend_score"))

    backend_score = backend_check(amount)

    fraud, final_score = final_fraud_score(frontend_score, backend_score)

    save_to_excel(name, user_id, amount, fraud, final_score)

    return jsonify({
        "fraud": fraud,
        "fraud_percent": final_score
    })

if __name__ == "__main__":
    init_excel()
    app.run(debug=True)