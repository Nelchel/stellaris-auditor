def build_campaign_narrative(report: dict) -> dict:
    old_audit = report.get("old_audit", {})
    new_audit = report.get("new_audit", {})
    timeline = report.get("timeline_analysis", {})

    if not old_audit or not new_audit:
        return {}

    old_strategy = old_audit.get("strategic_analysis", {})
    new_strategy = new_audit.get("strategic_analysis", {})
    old_meta = old_audit.get("meta_benchmarking", {})
    new_meta = new_audit.get("meta_benchmarking", {})

    old_year = old_meta.get("save_year", "?")
    new_year = new_meta.get("save_year", "?")
    old_arch = old_strategy.get("empire_archetype", "Unknown Empire")
    new_arch = new_strategy.get("empire_archetype", "Unknown Empire")

    growth = timeline.get("growth", {})
    score_delta = timeline.get("score_delta", {})

    economy_growth = growth.get("economy_core_growth_percent")
    trade_growth = growth.get("trade_income_growth_percent")
    military_growth = growth.get("military_power_growth_percent")
    empire_growth = growth.get("empire_size_growth_percent")
    stability_delta = score_delta.get("stability", 0)
    economy_delta = score_delta.get("economy", 0)
    military_delta = score_delta.get("military", 0)

    old_density = old_audit.get("metrics", {}).get("research", {}).get("research_density")
    new_density = new_audit.get("metrics", {}).get("research", {}).get("research_density")

    narrative = [
        f"Entre {old_year} et {new_year}, l’empire est passé de « {old_arch} » à « {new_arch} »."
    ]

    if economy_growth is not None and economy_growth > 80:
        narrative.append(f"La croissance économique a explosé (+{economy_growth}%), ce qui indique un vrai changement d’échelle.")
    elif economy_growth is not None and economy_growth > 25:
        narrative.append(f"L’économie progresse nettement (+{economy_growth}%), sans être totalement hors contrôle.")

    if military_growth is not None and military_growth > 150:
        narrative.append(f"La militarisation est massive (+{military_growth}% de puissance militaire), probablement alimentée par l’industrie et le trade.")
    elif military_growth is not None and military_growth > 50:
        narrative.append(f"La puissance militaire progresse fortement (+{military_growth}%).")

    if empire_growth is not None and empire_growth > 80:
        narrative.append(f"L’empire s’est énormément étendu (+{empire_growth}% d’empire size), ce qui augmente la pression administrative et scientifique.")

    if old_density is not None and new_density is not None and new_density < old_density:
        narrative.append(f"La densité scientifique se dégrade ({old_density} → {new_density}) : la science n’a pas suivi l’expansion.")

    if stability_delta < -20:
        narrative.append(f"La stabilité interne s’effondre ({stability_delta} points), signe que la croissance dépasse la capacité de gestion interne.")
    elif stability_delta < -5:
        narrative.append(f"La stabilité se dégrade ({stability_delta} points), à surveiller avant de continuer l’expansion.")

    turning_points = []

    if trade_growth is not None and trade_growth > 300:
        turning_points.append("Pivot majeur vers une économie de trade.")

    if military_growth is not None and military_growth > 150:
        turning_points.append("Militarisation rapide et changement de doctrine stratégique.")

    if empire_growth is not None and empire_growth > 80:
        turning_points.append("Expansion territoriale agressive.")

    if stability_delta < -20:
        turning_points.append("Dégradation brutale de la stabilité interne.")

    if old_arch != new_arch:
        turning_points.append(f"Changement d’archétype : {old_arch} → {new_arch}.")

    what_went_well = []

    if economy_delta > 10:
        what_went_well.append("La base économique a très fortement progressé.")

    if military_delta > 10:
        what_went_well.append("La puissance militaire est devenue crédible.")

    if new_meta.get("economy_curve") in ["Ahead", "Far Ahead"]:
        what_went_well.append("L’économie est au-dessus de la courbe benchmark.")

    if new_meta.get("military_curve") in ["Ahead", "Far Ahead"]:
        what_went_well.append("La puissance militaire est au-dessus de la courbe benchmark.")

    what_went_wrong = []
    flags = new_audit.get("risk_analysis", {}).get("detected_flags", {})

    if new_meta.get("research_curve") in ["Behind", "Far Behind"]:
        what_went_wrong.append("La recherche décroche par rapport au rythme de développement.")

    if stability_delta < -10:
        what_went_wrong.append("La stabilité interne a été sacrifiée pendant la croissance.")

    if flags.get("consumer_goods_deficit"):
        what_went_wrong.append("Le déficit de biens de consommation risque de freiner le scaling scientifique.")

    if flags.get("low_alloy_reserve"):
        what_went_wrong.append("La réserve d’alliages est trop basse malgré une bonne production.")

    if flags.get("economic_overextension"):
        what_went_wrong.append("L’empire semble économiquement sur-étendu : trop large pour sa base scientifique/interne.")

    next_pivot = []

    if new_meta.get("research_curve") in ["Behind", "Far Behind"]:
        next_pivot.append("Faire un pivot science : créer/convertir au moins une Tech World.")

    if new_audit.get("scores", {}).get("stability", 100) < 50:
        next_pivot.append("Stabiliser les planètes critiques avant nouvelle expansion.")

    if new_audit.get("resources", {}).get("stockpile", {}).get("alloys", 9999) < 500:
        next_pivot.append("Accumuler une réserve stratégique d’alliages avant guerre majeure.")

    if flags.get("consumer_goods_deficit"):
        next_pivot.append("Corriger les biens de consommation pour soutenir chercheurs et spécialistes.")

    if not next_pivot:
        next_pivot.append("Continuer le scaling, mais surveiller science et stabilité.")

    campaign_verdict = "Campagne en croissance forte."

    if stability_delta < -20 and new_meta.get("research_curve") in ["Behind", "Far Behind"]:
        campaign_verdict = "Campagne très puissante mais dangereusement déséquilibrée : l’économie et la flotte progressent plus vite que la science et la stabilité."
    elif new_meta.get("economy_curve") in ["Ahead", "Far Ahead"] and new_meta.get("research_curve") in ["Behind", "Far Behind"]:
        campaign_verdict = "Campagne économiquement dominante, mais technologiquement sous-scalée."
    elif new_audit.get("risk_analysis", {}).get("collapse_risk") == "Low":
        campaign_verdict = "Campagne saine : les risques restent contenus."

    return {
        "campaign_verdict": campaign_verdict,
        "main_trajectory": narrative,
        "turning_points": turning_points,
        "what_went_well": what_went_well,
        "what_went_wrong": what_went_wrong,
        "next_strategic_pivot": next_pivot,
        "summary": " ".join(narrative[:3]),
    }
