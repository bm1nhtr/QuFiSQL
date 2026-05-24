-- ============================================================
--  Quant Finance Database — Script de création MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS quant_finance
    CHARACTER SET utf8mb4        -- Encodage UTF-8 complet (4 octets), supporte tous les caractères Unicode
    COLLATE utf8mb4_unicode_ci;  -- Interclassement insensible à la casse, conforme Unicode
                                 -- (nécessaire car les données contiennent des caractères français : é, è, ê, ç...)

USE quant_finance;

-- ============================================================
--  DROP (ordre inverse des dépendances FK)
-- ============================================================
DROP TABLE IF EXISTS PrixHistorique;
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Position;
DROP TABLE IF EXISTS Instrument;
DROP TABLE IF EXISTS Portefeuille;
DROP TABLE IF EXISTS Client;
DROP TABLE IF EXISTS Gestionnaire;

-- ============================================================
--  1. Gestionnaire
-- ============================================================
CREATE TABLE Gestionnaire (
    id_gestionnaire INT          NOT NULL AUTO_INCREMENT,
    nom             VARCHAR(100) NOT NULL,
    prenom          VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL,
    date_embauche   DATE         NOT NULL,
    specialite      VARCHAR(100),

    CONSTRAINT pk_gestionnaire PRIMARY KEY (id_gestionnaire),
    CONSTRAINT uq_gestionnaire_email UNIQUE (email),
    CONSTRAINT chk_gestionnaire_email CHECK (email LIKE '%@%.%')
);

-- ============================================================
--  2. Client
-- ============================================================
CREATE TABLE Client (
    id_client       INT             NOT NULL AUTO_INCREMENT,
    nom             VARCHAR(100)    NOT NULL,
    prenom          VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL,
    aum             DECIMAL(18,2)   NOT NULL,
    profil_risque   ENUM('prudent','équilibré','dynamique','agressif') NOT NULL,
    date_entree     DATE            NOT NULL,
    id_gestionnaire INT             NOT NULL,

    CONSTRAINT pk_client          PRIMARY KEY (id_client),
    CONSTRAINT uq_client_email    UNIQUE (email),
    CONSTRAINT fk_client_gest     FOREIGN KEY (id_gestionnaire)
                                  REFERENCES Gestionnaire(id_gestionnaire)
                                  ON DELETE RESTRICT
                                  ON UPDATE CASCADE,
    CONSTRAINT chk_client_aum     CHECK (aum > 0),
    CONSTRAINT chk_client_aum_agressif CHECK (
        profil_risque <> 'agressif' OR aum >= 100000
    ),
    CONSTRAINT chk_client_email   CHECK (email LIKE '%@%.%')
);

-- ============================================================
--  3. Portefeuille
-- ============================================================
CREATE TABLE Portefeuille (
    id_portefeuille   INT             NOT NULL AUTO_INCREMENT,
    nom               VARCHAR(150)    NOT NULL,
    devise_base       CHAR(3)         NOT NULL,
    strategie         VARCHAR(100),
    date_creation     DATE            NOT NULL,
    valeur_liquidative DECIMAL(18,2)  NOT NULL DEFAULT 0,
    id_client         INT             NOT NULL,

    CONSTRAINT pk_portefeuille     PRIMARY KEY (id_portefeuille),
    CONSTRAINT fk_portef_client    FOREIGN KEY (id_client)
                                   REFERENCES Client(id_client)
                                   ON DELETE CASCADE
                                   ON UPDATE CASCADE,
    CONSTRAINT chk_portef_devise   CHECK (devise_base REGEXP '^[A-Z]{3}$'),
    CONSTRAINT chk_portef_vl       CHECK (valeur_liquidative >= 0)
);

-- ============================================================
--  4. Instrument
-- ============================================================
CREATE TABLE Instrument (
    id_instrument   INT             NOT NULL AUTO_INCREMENT,
    ticker          VARCHAR(20)     NOT NULL,
    nom             VARCHAR(150)    NOT NULL,
    type_instrument ENUM('action','obligation','ETF','dérivé') NOT NULL,
    secteur         VARCHAR(100),
    devise          CHAR(3)         NOT NULL,
    volatilite      DECIMAL(10,4)            DEFAULT 0,

    CONSTRAINT pk_instrument       PRIMARY KEY (id_instrument),
    CONSTRAINT uq_instrument_ticker UNIQUE (ticker),
    CONSTRAINT chk_instrument_devise    CHECK (devise REGEXP '^[A-Z]{3}$'),
    CONSTRAINT chk_instrument_volatilite CHECK (volatilite >= 0)
);

-- ============================================================
--  5. Position  (clé primaire composite)
-- ============================================================
CREATE TABLE Position (
    id_portefeuille INT           NOT NULL,
    id_instrument   INT           NOT NULL,
    date_valo       DATE          NOT NULL,
    quantite        DECIMAL(18,6) NOT NULL,
    prix_moyen      DECIMAL(18,4) NOT NULL,
    poids           DECIMAL(5,4)  NOT NULL DEFAULT 0,
    pnl_latent      DECIMAL(18,2) NOT NULL DEFAULT 0,

    CONSTRAINT pk_position PRIMARY KEY (id_portefeuille, id_instrument, date_valo),
    CONSTRAINT fk_pos_portef  FOREIGN KEY (id_portefeuille)
                              REFERENCES Portefeuille(id_portefeuille)
                              ON DELETE CASCADE
                              ON UPDATE CASCADE,
    CONSTRAINT fk_pos_instrum FOREIGN KEY (id_instrument)
                              REFERENCES Instrument(id_instrument)
                              ON DELETE RESTRICT
                              ON UPDATE CASCADE,
    CONSTRAINT chk_pos_quantite    CHECK (quantite > 0),
    CONSTRAINT chk_pos_prix_moyen  CHECK (prix_moyen > 0),
    CONSTRAINT chk_pos_poids       CHECK (poids BETWEEN 0 AND 1)
);

-- ============================================================
--  6. PrixHistorique
-- ============================================================
CREATE TABLE PrixHistorique (
    id_prix         INT             NOT NULL AUTO_INCREMENT,
    date_cotation   DATE            NOT NULL,
    cours_cloture   DECIMAL(18,4)   NOT NULL,
    volume          BIGINT                   DEFAULT 0,
    rendement_jour  DECIMAL(10,6),
    id_instrument   INT             NOT NULL,

    CONSTRAINT pk_prix             PRIMARY KEY (id_prix),
    CONSTRAINT uq_prix_ticker_date UNIQUE (id_instrument, date_cotation),
    CONSTRAINT fk_prix_instrum     FOREIGN KEY (id_instrument)
                                   REFERENCES Instrument(id_instrument)
                                   ON DELETE CASCADE
                                   ON UPDATE CASCADE,
    CONSTRAINT chk_prix_cloture    CHECK (cours_cloture > 0),
    CONSTRAINT chk_prix_volume     CHECK (volume >= 0)
);

-- ============================================================
--  7. Transaction
-- ============================================================
CREATE TABLE Transaction (
    id_transaction  INT             NOT NULL AUTO_INCREMENT,
    sens            ENUM('ACHAT','VENTE') NOT NULL,
    quantite        DECIMAL(18,6)   NOT NULL,
    prix_execution  DECIMAL(18,4)   NOT NULL,
    date_transaction DATE           NOT NULL,
    frais           DECIMAL(18,2)   NOT NULL DEFAULT 0,
    id_portefeuille INT             NOT NULL,
    id_instrument   INT             NOT NULL,

    CONSTRAINT pk_transaction      PRIMARY KEY (id_transaction),
    CONSTRAINT fk_txn_portef       FOREIGN KEY (id_portefeuille)
                                   REFERENCES Portefeuille(id_portefeuille)
                                   ON DELETE RESTRICT
                                   ON UPDATE CASCADE,
    CONSTRAINT fk_txn_instrum      FOREIGN KEY (id_instrument)
                                   REFERENCES Instrument(id_instrument)
                                   ON DELETE RESTRICT
                                   ON UPDATE CASCADE,
    CONSTRAINT chk_txn_quantite    CHECK (quantite > 0),
    CONSTRAINT chk_txn_prix        CHECK (prix_execution > 0),
    CONSTRAINT chk_txn_frais       CHECK (
        frais >= 0 AND frais <= prix_execution * quantite * 0.05
    )
);