from flask import Flask, render_template, jsonify, Response
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# Token de autenticação exigido pelo endpoint
HEADERS = {
    "Authorization": "ProcessoSeletivoStract2025"
}


# URL base da API externa
BASE_URL = "https://sidebar.stract.to/api/"

# Função para buscar contas de qualquer plataforma (GA4, Meta Ads, TikTok Insights, etc.)
def get_all_accounts_by_platform(platform):
    all_data = []
    page = 1  

    while True:
        response = requests.get(f"{BASE_URL}accounts?platform={platform}&page={page}", headers=HEADERS)

        if response.status_code != 200:
            return {"error": f"Falha ao acessar API de contas para {platform}", "status_code": response.status_code}

        data = response.json()
        all_data.extend(data.get("accounts", []))

        current_page = data.get("pagination", {}).get("current", 1)
        total_pages = data.get("pagination", {}).get("total", 1)

        if current_page >= total_pages:
            break  

        page += 1  

    return all_data

# Função para buscar insights de qualquer plataforma (GA4, Meta Ads, TikTok Insights, etc.)
def get_insights_for_accounts(platform):
    accounts = get_all_accounts_by_platform(platform)

    if "error" in accounts:
        return accounts 

    insights_data = []

    # Percorre cada conta e busca os insights usando ID e Token
    for account in accounts:
        insights_url = f"{BASE_URL}insights?platform={platform}&account={account['id']}&token={account['token']}&fields=adName,impressions,cost,region,clicks,status"
        response = requests.get(insights_url, headers=HEADERS)

        if response.status_code == 200:
            insights = response.json()
            insights_data.append({
                "platform": platform,
                "id": account["id"],
                "name": account["name"],
                "token": account["token"],
                "insights": insights  # Adiciona os insights completos da conta
            })
        else:
            insights_data.append({
                "platform": platform,
                "id": account["id"],
                "name": account["name"],
                "token": account["token"],
                "error": f"Falha ao acessar insights para {platform}",
                "status_code": response.status_code
            })

    return insights_data

# Endpoint para buscar insights de qualquer plataforma
@app.route("/<platform>")
def get_insights(platform):
    insights_data = get_insights_for_accounts(platform)

    if "error" in insights_data:
        return jsonify(insights_data), 500

    return render_template("insights.html", insights=insights_data, platform=platform)

@app.route("/<platform>/resumo")
def get_insights_summary(platform):
    insights_data = get_insights_for_accounts(platform)

    if isinstance(insights_data, dict) and "error" in insights_data:
        return jsonify(insights_data), 500

    summary_data = {}

    for insight in insights_data:
        account_name = insight["name"]
        if account_name not in summary_data:
            summary_data[account_name] = {
                "platform": platform,
                "name": account_name,
                "clicks": 0,
                "cost": 0,
                "impressions": 0,
                "region": "",
                "status": ""
            }

        for ad in insight["insights"]["insights"]:
            summary_data[account_name]["clicks"] += ad.get("clicks", 0)
            summary_data[account_name]["cost"] += ad.get("cost", 0)
            summary_data[account_name]["impressions"] += ad.get("impressions", 0)

    return render_template("summary.html", platform=platform, insights=summary_data.values())

@app.route("/geral")
def get_all_insights():
    platforms = ["ga4", "meta_ads", "tiktok_insights"]
    all_insights = []

    for platform in platforms:
        insights_data = get_insights_for_accounts(platform)

        if isinstance(insights_data, dict) and "error" in insights_data:
            return jsonify(insights_data), 500

        for insight in insights_data:
            account_name = insight["name"]

            for ad in insight["insights"]["insights"]:
                # Criar estrutura padronizada
                row = {
                    "platform": platform.capitalize(),
                    "account_name": account_name,
                    "adName": ad.get("adName", ""),
                    "clicks": ad.get("clicks", ""),
                    "cost": ad.get("cost", ""),
                    "impressions": ad.get("impressions", ""),
                    "region": ad.get("region", ""),
                    "status": ad.get("status", ""),
                    "cost_per_click": ""  # Calculado se houver 'cost' e 'clicks'
                }

                # Se "cost" e "clicks" existirem, calcular "Cost per Click"
                if "cost" in ad and "clicks" in ad and ad["clicks"] > 0:
                    row["cost_per_click"] = round(ad["cost"] / ad["clicks"], 2)

                all_insights.append(row)

    return render_template("general.html", platform="Geral", insights=all_insights)

@app.route("/geral/resumo")
def get_general_summary():
    platforms = ["ga4", "meta_ads", "tiktok_insights"]
    summary_data = {}

    for platform in platforms:
        insights_data = get_insights_for_accounts(platform)

        if isinstance(insights_data, dict) and "error" in insights_data:
            return jsonify(insights_data), 500

        for insight in insights_data:
            if platform not in summary_data:
                summary_data[platform] = {
                    "platform": platform.capitalize(),
                    "clicks": 0,
                    "cost": 0,
                    "impressions": 0,
                    "cost_per_click": ""  # Calculado depois, se houver "clicks"
                }

            for ad in insight["insights"]["insights"]:
                summary_data[platform]["clicks"] += ad.get("clicks", 0)
                summary_data[platform]["cost"] += ad.get("cost", 0)
                summary_data[platform]["impressions"] += ad.get("impressions", 0)

            # Calcular "Cost per Click" se houver "clicks" válidos
            if summary_data[platform]["clicks"] > 0:
                summary_data[platform]["cost_per_click"] = round(
                    summary_data[platform]["cost"] / summary_data[platform]["clicks"], 2
                )

    return render_template("general_summary.html", insights=summary_data.values())



if __name__ == "__main__":
    app.run(debug=True)