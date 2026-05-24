-- ============================================================
-- R1 — Liste simple : tous les instruments triés par nom
-- Tables  : Instrument
-- ============================================================
SELECT
    id_instrument,
    ticker,
    nom,
    type_instrument,
    secteur,
    devise
FROM Instrument
ORDER BY nom ASC;

-- ============================================================
-- R2 — Filtre WHERE : clients dont l'AUM dépasse 100 000 €
-- Tables  : Client
-- ============================================================
SELECT
    id_client,
    nom,
    prenom,
    email,
    aum,
    profil_risque
FROM Client
WHERE aum > 100000
ORDER BY aum DESC;

-- ============================================================
-- R3 — Filtre paramétrique : transactions d'un portefeuille donné
-- Tables  : Transaction
-- Paramètre : id_portefeuille = 3
-- ============================================================
SELECT
    id_transaction,
    sens,
    quantite,
    prix_execution,
    date_transaction,
    frais,
    id_instrument
FROM Transaction
WHERE id_portefeuille = 3
ORDER BY date_transaction ASC;

-- ============================================================
-- R4 — JOIN simple : positions enrichies avec les infos instrument
-- Tables  : Position INNER JOIN Instrument
-- Filtre  : date_valo = '2024-12-04'
-- ============================================================
SELECT
    po.id_portefeuille,
    i.ticker,
    i.nom                   AS instrument,
    i.type_instrument,
    i.secteur,
    po.quantite,
    po.prix_moyen,
    po.poids,
    po.pnl_latent
FROM Position po
INNER JOIN Instrument i ON po.id_instrument = i.id_instrument
WHERE po.date_valo = '2024-12-04'
ORDER BY po.id_portefeuille, po.poids DESC;

-- ============================================================
-- R5 — LEFT JOIN : instruments avec ou sans transaction
--          (les instruments sans transaction apparaissent en premier)
-- Tables  : Instrument LEFT JOIN Transaction
-- ============================================================
SELECT
    i.id_instrument,
    i.ticker,
    i.nom,
    i.type_instrument,
    t.id_transaction        -- NULL si aucune transaction
FROM Instrument i
LEFT JOIN Transaction t ON i.id_instrument = t.id_instrument
ORDER BY t.id_transaction IS NULL DESC, i.ticker ASC;

-- ============================================================
-- R6 — GROUP BY + agrégats : montant total des ACHATS par type d'instrument
-- Tables  : Transaction INNER JOIN Instrument
-- Filtre  : sens = 'ACHAT'
-- ============================================================
SELECT
    i.type_instrument,
    COUNT(t.id_transaction)                        AS nb_transactions,
    ROUND(SUM(t.quantite * t.prix_execution), 2)   AS montant_total_investi,
    ROUND(AVG(t.prix_execution), 4)                AS prix_moyen_execution
FROM Transaction t
INNER JOIN Instrument i ON t.id_instrument = i.id_instrument
WHERE t.sens = 'ACHAT'
GROUP BY i.type_instrument
ORDER BY montant_total_investi DESC;

-- ============================================================
-- R7 — GROUP BY avec JOIN : nombre de positions et somme des poids
--          par portefeuille à une date de valorisation
-- Tables  : Position INNER JOIN Portefeuille
-- Filtre  : date_valo = '2024-12-04'
-- ============================================================
SELECT
    po.id_portefeuille,
    p.nom                     AS nom_portefeuille,
    COUNT(*)                  AS nb_positions,
    ROUND(SUM(po.poids), 4)   AS somme_poids
FROM Position po
INNER JOIN Portefeuille p ON po.id_portefeuille = p.id_portefeuille
WHERE po.date_valo = '2024-12-04'
GROUP BY po.id_portefeuille, p.nom
ORDER BY nb_positions DESC;

-- ============================================================
-- R8 — GROUP BY + HAVING : gestionnaires gérant au moins 2 clients
-- Tables  : Gestionnaire INNER JOIN Client
-- ============================================================
SELECT
    g.id_gestionnaire,
    g.nom,
    g.prenom,
    g.specialite,
    COUNT(c.id_client) AS nb_clients
FROM Gestionnaire g
INNER JOIN Client c ON g.id_gestionnaire = c.id_gestionnaire
GROUP BY g.id_gestionnaire, g.nom, g.prenom, g.specialite
HAVING COUNT(c.id_client) >= 2
ORDER BY nb_clients DESC;

-- ============================================================
-- R9 — GROUP BY + HAVING sur agrégat : types d'instruments
--          dont le PnL latent moyen dépasse 500
-- Tables  : Position INNER JOIN Instrument
-- Filtre  : date_valo = '2024-12-04'
-- ============================================================
SELECT
    i.type_instrument,
    COUNT(*)                       AS nb_positions,
    ROUND(AVG(po.pnl_latent), 2)   AS pnl_moyen,
    ROUND(SUM(po.pnl_latent), 2)   AS pnl_total
FROM Position po
INNER JOIN Instrument i ON po.id_instrument = i.id_instrument
WHERE po.date_valo = '2024-12-04'
GROUP BY i.type_instrument
HAVING AVG(po.pnl_latent) > 500
ORDER BY pnl_moyen DESC;

-- ============================================================
-- R10 — GROUP BY + MIN/MAX : amplitude de cours par instrument
--           sur l'historique des prix (variation min → max en %)
-- Tables  : PrixHistorique INNER JOIN Instrument
-- ============================================================
SELECT
    i.ticker,
    i.nom,
    i.type_instrument,
    MIN(ph.cours_cloture)                              AS cours_min,
    MAX(ph.cours_cloture)                              AS cours_max,
    ROUND(MAX(ph.cours_cloture)
          - MIN(ph.cours_cloture), 4)                  AS amplitude,
    ROUND((MAX(ph.cours_cloture)
           - MIN(ph.cours_cloture))
          / MIN(ph.cours_cloture) * 100, 2)            AS amplitude_pct
FROM PrixHistorique ph
INNER JOIN Instrument i ON ph.id_instrument = i.id_instrument
GROUP BY i.id_instrument, i.ticker, i.nom, i.type_instrument
ORDER BY amplitude_pct DESC;

-- ============================================================
-- R11 — Sous-requête scalaire : portefeuilles dont la VL est
--           supérieure à la moyenne, avec écart calculé
-- Tables  : Portefeuille (sous-requête sur la même table)
-- ============================================================
SELECT
    id_portefeuille,
    nom,
    devise_base,
    strategie,
    valeur_liquidative,
    ROUND(valeur_liquidative - (
        SELECT AVG(valeur_liquidative) FROM Portefeuille
    ), 2)  AS ecart_a_la_moyenne
FROM Portefeuille
WHERE valeur_liquidative > (
    SELECT AVG(valeur_liquidative)
    FROM   Portefeuille
)
ORDER BY valeur_liquidative DESC;

-- ============================================================
-- R12 — EXISTS / NOT EXISTS : instruments achetés mais jamais vendus
-- Tables  : Instrument, Transaction (sous-requêtes corrélées)
-- ============================================================
SELECT
    i.id_instrument,
    i.ticker,
    i.nom,
    i.type_instrument,
    i.secteur
FROM Instrument i
WHERE EXISTS (
    SELECT 1
    FROM   Transaction t
    WHERE  t.id_instrument = i.id_instrument
    AND    t.sens = 'ACHAT'
)
AND NOT EXISTS (
    SELECT 1
    FROM   Transaction t
    WHERE  t.id_instrument = i.id_instrument
    AND    t.sens = 'VENTE'
)
ORDER BY i.type_instrument, i.ticker;

-- ============================================================
-- R13 — ORDER BY multi-critères : portefeuilles triés par VL décroissante,
--           puis par date de création (départage)
-- Tables  : Portefeuille
-- ============================================================
SELECT
    id_portefeuille,
    nom,
    valeur_liquidative,
    date_creation
FROM Portefeuille
ORDER BY
    valeur_liquidative DESC,
    date_creation      ASC;

-- ============================================================
-- R14 — Sous-requête IN + HAVING : portefeuilles ayant tradé
--           au moins 2 types d'instruments différents
-- Tables  : Portefeuille, Transaction, Instrument
-- ============================================================
SELECT
    p.id_portefeuille,
    p.nom
FROM Portefeuille p
WHERE p.id_portefeuille IN (
    SELECT      t.id_portefeuille
    FROM        Transaction  t
    JOIN        Instrument   i ON t.id_instrument = i.id_instrument
    GROUP BY    t.id_portefeuille
    HAVING      COUNT(DISTINCT i.type_instrument) >= 2
)
ORDER BY p.id_portefeuille;

-- ============================================================
-- R15 — Sous-requête + JOIN : instruments les plus volatils
--           de chaque type (volatilite = MAX par type_instrument)
-- Tables  : Instrument (sous-requête agrégée sur Instrument)
-- ============================================================
SELECT
    i.type_instrument,
    i.ticker,
    i.nom,
    i.volatilite
FROM Instrument i
JOIN (
    SELECT
        type_instrument,
        MAX(volatilite) AS vol_max
    FROM  Instrument
    GROUP BY type_instrument
) max_vol
    ON  i.type_instrument = max_vol.type_instrument
    AND i.volatilite      = max_vol.vol_max
ORDER BY
    i.type_instrument ASC,
    i.ticker          ASC;
