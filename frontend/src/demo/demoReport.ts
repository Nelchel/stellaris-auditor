export const demoReport = {
  "mode": "timeline",
  "data": {
    "version": "3.5-demo",
    "old_audit": {
      "scores": {
        "global": 61,
        "economy": 72,
        "military": 37,
        "research": 51,
        "expansion": 60,
        "stability": 85
      },
      "meta_benchmarking": {
        "save_year": 2242,
        "benchmark_reference_year": 2250,
        "research_curve": "On Curve",
        "military_curve": "Behind",
        "economy_curve": "Ahead",
        "overall_meta_position": "Empire équilibré mais encore peu militarisé."
      },
      "metrics": {
        "research": {
          "research_total": 204.9,
          "research_density": 1.132
        },
        "military": {
          "military_power": 2275.03
        },
        "empire": {
          "empire_size": 181
        }
      },
      "resources": {
        "income": {
          "energy": 610,
          "minerals": 205,
          "alloys": 81,
          "trade": 260
        }
      },
      "risk_analysis": {
        "overall_risk_score": 9,
        "collapse_risk": "Low"
      },
      "strategic_analysis": {
        "empire_archetype": "Balanced Empire"
      },
      "planet_specialization_summary": {
        "Tech World": 1,
        "Generator World": 1,
        "Agri World": 2
      },
      "planets": []
    },
    "new_audit": {
      "scores": {
        "global": 64,
        "economy": 95,
        "military": 77,
        "research": 49,
        "expansion": 70,
        "stability": 27
      },
      "strategic_analysis": {
        "empire_archetype": "Trade-Industrial-Militarist-Internally-Unstable Empire",
        "verdict": "Empire très riche, mais qui ne transforme pas assez sa puissance économique en avance scientifique.",
        "priority_actions": [
          "Créer ou convertir au moins une planète en Tech World.",
          "Corriger les amenities négatives sur les planètes critiques.",
          "Accumuler une réserve stratégique d’alliages."
        ]
      },
      "risk_analysis": {
        "overall_risk_score": 42,
        "collapse_risk": "Medium",
        "war_readiness": "Good but low reserves",
        "verdict": "Empire puissant mais sous tension interne.",
        "detected_flags": {
          "consumer_goods_deficit": true,
          "low_alloy_reserve": true,
          "economic_overextension": true
        }
      },
      "meta_benchmarking": {
        "save_year": 2285,
        "benchmark_reference_year": 2275,
        "research_curve": "Behind",
        "military_curve": "Ahead",
        "economy_curve": "Far Ahead",
        "overall_meta_position": "Économiquement en avance, scientifiquement en retard, militairement solide."
      },
      "metrics": {
        "research": {
          "research_total": 336.69,
          "research_density": 0.838
        },
        "military": {
          "military_power": 11658.97
        },
        "empire": {
          "empire_size": 402
        }
      },
      "resources": {
        "income": {
          "energy": 1110.96,
          "minerals": 442.22,
          "alloys": 81.83,
          "trade": 1603.53
        }
      },
      "planet_specialization_summary": {
        "Forge World": 4,
        "Generator World": 2,
        "Industrial World": 1,
        "Tech World": 1,
        "Unknown": 3
      },
      "top_problem_planets": [
        {
          "id": "4759",
          "display_name": "Planet 4759",
          "specialization_guess": "Forge World",
          "efficiency_score": 50,
          "stability": 26.877,
          "free_amenities_normalized": -4.86,
          "alerts": [
            "stabilité basse",
            "amenities insuffisantes"
          ],
          "specialization_issues": [
            "Forge World sous-supportée : amenities insuffisantes pour l’industrie lourde."
          ],
          "profitability_score": 25,
          "economic_status": "Economic Sink",
          "economic_recommendations": [
            "Ajouter amenities/support avant de continuer l’industrialisation.",
            "Stabiliser la planète avant tout investissement supplémentaire."
          ]
        },
        {
          "id": "5447",
          "display_name": "Planet 5447",
          "specialization_guess": "Forge World",
          "efficiency_score": 50,
          "stability": 22.049,
          "free_amenities_normalized": -3.65,
          "alerts": [
            "stabilité basse",
            "amenities insuffisantes"
          ],
          "specialization_issues": [
            "Forge World instable : risque de perte de rendement industriel."
          ],
          "profitability_score": 25,
          "economic_status": "Economic Sink",
          "economic_recommendations": [
            "Ajouter amenities/support avant de continuer l’industrialisation."
          ]
        }
      ],
      "planet_intelligence": {
        "summary": "Les mondes industriels/forge concentrent la pression interne : l’économie lourde dépasse le support planétaire.",
        "pressure_summary": {
          "Critical": 2,
          "High": 2,
          "Medium": 1,
          "Low": 6
        },
        "worst_planets": [
          {
            "id": "4759",
            "display_name": "Planet 4759",
            "specialization_guess": "Forge World",
            "efficiency_score": 50,
            "stability": 26.877,
            "free_amenities_normalized": -4.86,
            "specialization_issues": [
              "Efficacité faible pour sa spécialisation.",
              "Forge World sous-supportée : amenities insuffisantes pour l’industrie lourde."
            ],
            "profitability_score": 25,
            "economic_status": "Economic Sink",
            "economic_recommendations": [
              "Ajouter amenities/support avant de continuer l’industrialisation."
            ]
          },
          {
            "id": "5447",
            "display_name": "Planet 5447",
            "specialization_guess": "Forge World",
            "efficiency_score": 50,
            "stability": 22.049,
            "free_amenities_normalized": -3.65,
            "specialization_issues": [
              "Efficacité faible pour sa spécialisation.",
              "Forge World instable : risque de perte de rendement industriel."
            ],
            "profitability_score": 25,
            "economic_status": "Economic Sink",
            "economic_recommendations": [
              "Stabiliser la planète avant tout investissement supplémentaire."
            ]
          }
        ],
        "best_planets": [
          {
            "id": "11",
            "display_name": "Planet 11",
            "specialization_guess": "Tech World",
            "efficiency_score": 100,
            "stability": 77.348,
            "free_amenities_normalized": 29.54
          },
          {
            "id": "9038",
            "display_name": "Planet 9038",
            "specialization_guess": "Agri World",
            "efficiency_score": 100,
            "stability": 74.069,
            "free_amenities_normalized": 0.82
          }
        ],
        "specialization_issues": [
          {
            "id": "4759",
            "display_name": "Planet 4759",
            "specialization_guess": "Forge World",
            "efficiency_score": 50,
            "stability": 26.877,
            "free_amenities_normalized": -4.86,
            "specialization_issues": [
              "Efficacité faible pour sa spécialisation.",
              "Forge World sous-supportée : amenities insuffisantes pour l’industrie lourde."
            ]
          },
          {
            "id": "5447",
            "display_name": "Planet 5447",
            "specialization_guess": "Forge World",
            "efficiency_score": 50,
            "stability": 22.049,
            "free_amenities_normalized": -3.65,
            "specialization_issues": [
              "Forge World instable : risque de perte de rendement industriel."
            ]
          }
        ]
      }
    },
    "timeline_analysis": {
      "growth": {
        "economy_core_growth_percent": 131.2,
        "military_power_growth_percent": 412.48,
        "empire_size_growth_percent": 122.1,
        "research_growth_percent": 64.3,
        "trade_income_growth_percent": 516.74
      },
      "score_delta": {
        "economy": 23,
        "military": 40,
        "research": -2,
        "stability": -58,
        "global": 3
      },
      "metric_delta": {}
    },
    "evolution_analysis": {
      "score_deltas": {
        "economy": {
          "old": 72,
          "new": 95,
          "delta": 23
        },
        "military": {
          "old": 37,
          "new": 77,
          "delta": 40
        },
        "research": {
          "old": 51,
          "new": 49,
          "delta": -2
        },
        "stability": {
          "old": 85,
          "new": 27,
          "delta": -58
        },
        "global": {
          "old": 61,
          "new": 64,
          "delta": 3
        }
      },
      "insights": [
        "L’économie globale progresse correctement.",
        "La stabilité empire : expansion ou pression interne trop forte.",
        "La puissance militaire augmente rapidement."
      ],
      "planet_changes": {
        "improved": [],
        "worsened": []
      }
    },
    "campaign_narrative": {
      "campaign_verdict": "Campagne très puissante mais dangereusement déséquilibrée : l’économie et la flotte progressent plus vite que la science et la stabilité.",
      "summary": "Entre 2242 et 2285, l’empire est passé de « Balanced Empire » à « Trade-Industrial-Militarist-Internally-Unstable Empire ». La croissance économique a explosé (+131.2%), ce qui indique un vrai changement d’échelle. La militarisation est massive (+412.48% de puissance militaire), probablement alimentée par l’industrie et le trade.",
      "main_trajectory": [
        "Entre 2242 et 2285, l’empire est passé de « Balanced Empire » à « Trade-Industrial-Militarist-Internally-Unstable Empire ».",
        "La croissance économique a explosé (+131.2%), ce qui indique un vrai changement d’échelle.",
        "La militarisation est massive (+412.48% de puissance militaire), probablement alimentée par l’industrie et le trade.",
        "La stabilité interne s’effondre (-58 points), signe que la croissance dépasse la capacité de gestion interne."
      ],
      "what_went_well": [
        "La base économique a très fortement progressé.",
        "La puissance militaire est devenue crédible.",
        "L’économie est au-dessus de la courbe benchmark."
      ],
      "what_went_wrong": [
        "La recherche décroche par rapport au rythme de développement.",
        "La stabilité interne a été sacrifiée pendant la croissance.",
        "Le déficit de biens de consommation risque de freiner le scaling scientifique."
      ],
      "turning_points": [
        "Pivot majeur vers une économie de trade.",
        "Militarisation rapide et changement de doctrine stratégique.",
        "Dégradation brutale de la stabilité interne."
      ],
      "next_strategic_pivot": [
        "Faire un pivot science : créer/convertir au moins une Tech World.",
        "Stabiliser les planètes critiques avant nouvelle expansion.",
        "Accumuler une réserve stratégique d’alliages avant guerre majeure."
      ]
    },
    "visual_analytics": {
      "labels": [
        "2242",
        "2285"
      ],
      "score_radar_old": [
        72,
        37,
        51,
        60,
        85
      ],
      "score_radar_new": [
        95,
        77,
        49,
        70,
        27
      ],
      "scores_over_time": {
        "global": [
          61,
          64
        ],
        "economy": [
          72,
          95
        ],
        "military": [
          37,
          77
        ],
        "research": [
          51,
          49
        ],
        "stability": [
          85,
          27
        ]
      },
      "core_metrics": {
        "economy_core": [
          896,
          1635
        ],
        "research_total": [
          204.9,
          336.69
        ],
        "military_power": [
          2275.03,
          11658.97
        ],
        "empire_size": [
          181,
          402
        ]
      },
      "risk_vs_stability": {
        "risk": [
          9,
          42
        ],
        "stability": [
          85,
          27
        ]
      },
      "research_pressure": {
        "research_density": [
          1.132,
          0.838
        ],
        "empire_size": [
          181,
          402
        ]
      },
      "specialization_shift": {
        "labels": [
          "Agri World",
          "Forge World",
          "Generator World",
          "Industrial World",
          "Tech World",
          "Unknown"
        ],
        "old": [
          2,
          0,
          1,
          0,
          1,
          0
        ],
        "new": [
          0,
          4,
          2,
          1,
          1,
          3
        ]
      }
    }
  }
}
