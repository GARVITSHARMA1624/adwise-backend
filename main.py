from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SellerInput(BaseModel):
    product_cost: float
    selling_price: float
    shipping_cost: float
    packaging_cost: float
    daily_ad_spend: float
    orders_per_day: int


@app.get("/")
def home():
    return {"status": "Instagram Profit Advisor is running"}


@app.post("/analyze")
def analyze(data: SellerInput):
    # --- Core Calculations ---
    ad_cost_per_order = data.daily_ad_spend / data.orders_per_day

    total_cost = (
        data.product_cost
        + data.shipping_cost
        + data.packaging_cost
        + ad_cost_per_order
    )

    profit_per_order = data.selling_price - total_cost
    profit_margin = (profit_per_order / data.selling_price) * 100

    warnings = []

    # --- Risk Classification ---
    if profit_per_order < 0:
        risk = "LOSS"
        base_advice = "You are losing money on every order. Stop selling this product immediately."
    elif profit_margin < 20:
        risk = "RISKY"
        base_advice = "You are making profit, but the margin is very low. This product is risky on Instagram."
    else:
        risk = "SAFE"
        base_advice = "This product is profitable and relatively safe to sell on Instagram."

    # --- Instagram-Specific Warnings ---

    # Heavy ad dependency
    if (ad_cost_per_order / data.selling_price) > 0.30:
        warnings.append(
            "Your profit depends heavily on ads. If ad costs increase, profits will drop quickly."
        )

    # Low price warning
    if data.selling_price < 799:
        warnings.append(
            "Low-priced products are risky on Instagram because ads and returns eat profit."
        )

    # Thin margin warning
    if 20 <= profit_margin <= 30:
        warnings.append(
            "Your margin is thin. One return can wipe profit from multiple orders."
        )

    # --- Final Advice ---
    full_advice = base_advice
    if warnings:
        full_advice += " Important notes: " + " ".join(warnings)

    return {
        "profit_per_order": round(profit_per_order, 2),
        "profit_margin_percent": round(profit_margin, 2),
        "risk_level": risk,
        "advice": full_advice
    }
