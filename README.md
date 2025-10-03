📊 Sector Rotation Strategy — CAC40

🔎 Description

Ce projet met en œuvre une stratégie systématique de sector rotation appliquée au CAC40.
L’idée est simple :
	•	Chaque mois, on classe les actions du CAC40 selon un score basé sur le momentum 3-1 mois (performance passée à moyen terme) ajusté par la volatilité.
	•	On sélectionne les 5 meilleures actions issues de secteurs différents pour assurer une diversification.
	•	Le portefeuille est rebalancé mensuellement : certains titres sortent, d’autres entrent.
	•	En cas de tendance de marché défavorable (filtre macro via le CAC40 ou le VIX), une partie du portefeuille peut être mise en cash pour réduire le drawdown.

Cette approche s’inspire des méthodes utilisées dans les hedge funds :
👉 capter les tendances fortes tout en contrôlant le risque.

⸻

⚙️ Méthodologie
	1.	Momentum 3-1 mois
	•	Performance des 3 derniers mois en excluant le dernier mois (effet de retour court terme).
	2.	Ajustement par volatilité
	•	Les titres trop volatils sont pénalisés (ratio momentum/vol).
	3.	Sélection des Top 5
	•	Diversifiés par secteur.
	•	Pondération égale ou pondérée par le score.
	4.	Cash management
	•	Quand la tendance du marché (CAC40) est en dessous de sa Moyenne Mobile 10 mois, une partie du portefeuille est allouée au cash.

⸻

📈 Résultats (2018–2025, backtest)
	•	Stratégie (Top 5, mom3-1/vol, cash filter)
	•	Ann. Return : ~9%
	•	Sharpe Ratio : ~0.60–0.70
	•	Max Drawdown : ~-20%
	•	Benchmark (CAC40)
	•	Ann. Return : ~5%
	•	Sharpe Ratio : ~0.35
	•	Max Drawdown : ~-26%

👉 La stratégie améliore nettement le rendement ajusté du risque par rapport à un buy-and-hold
