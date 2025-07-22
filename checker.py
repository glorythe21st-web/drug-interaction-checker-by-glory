import requests
import csv
import tkinter as tk
from tkinter import messagebox

def fetch_rxcui(drug_name):
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("idGroup", {}).get("rxnormId", [None])[0]
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error fetching RxCUI for {drug_name}: {e}")
        return None

def check_interaction(rxcui_list):
    url = f"https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis={'+'.join(rxcui_list)}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        interactions = []

        full_interactions = data.get("fullInteractionTypeGroup", [])
        for group in full_interactions:
            for interaction_type in group.get("fullInteractionType", []):
                for interaction_pair in interaction_type.get("interactionPair", []):
                    interaction = {
                        "description": interaction_pair.get("description", ""),
                        "severity": interaction_pair.get("severity", ""),
                        "source": interaction_pair.get("source", ""),
                    }
                    interactions.append(interaction)

        return interactions
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error checking interactions: {e}")
        return []

def save_to_csv(data, filename="drug_interactions.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["description", "severity", "source"])
        writer.writeheader()
        for item in data:
            writer.writerow(item)

def on_check():
    user_input = entry.get()
    drugs = [drug.strip() for drug in user_input.split(",") if drug.strip()]
    if not drugs:
        messagebox.showwarning("Input Error", "Please enter at least one drug name.")
        return

    rxcuis = [fetch_rxcui(drug) for drug in drugs]
    rxcuis = [r for r in rxcuis if r]

    if not rxcuis:
        messagebox.showinfo("No Results", "No RxCUIs found.")
        return

    interactions = check_interaction(rxcuis)
    if interactions:
        result_text.delete("1.0", tk.END)
        for i in interactions:
            result_text.insert(tk.END, f"{i['description']} (Severity: {i['severity']}, Source: {i['source']})\n")
        save_to_csv(interactions)
    else:
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, "✅ No known interactions found.\n")

# Setup GUI
root = tk.Tk()
root.title("Drug Interaction Checker")

tk.Label(root, text="Enter drug names separated by commas:").pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack(pady=5)

tk.Button(root, text="Check Interactions", command=on_check).pack(pady=10)
result_text = tk.Text(root, width=80, height=15)
result_text.pack(pady=5)

root.mainloop()
