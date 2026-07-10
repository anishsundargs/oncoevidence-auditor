from pathlib import Path
import pandas as pd


REGISTRY_PATH = Path("data/config/cancer_registry.csv")
MOCK_PATH = Path("data/mock_gene_evidence.csv")
ROLE_PATH = Path("data/config/gene_role_annotations.csv")
PATHWAY_PATH = Path("data/config/pathway_function_annotations.csv")
THER_PATH = Path("data/config/therapeutic_relevance_annotations.csv")


def upsert(df, rows, keys):
    rows_df = pd.DataFrame(rows)

    for col in rows_df.columns:
        if col not in df.columns:
            df[col] = None

    for col in df.columns:
        if col not in rows_df.columns:
            rows_df[col] = None

    key_tuples = set(tuple(row[k] for k in keys) for row in rows)

    keep_mask = ~df.apply(
        lambda r: tuple(r[k] for k in keys) in key_tuples,
        axis=1,
    )

    return pd.concat([df[keep_mask], rows_df[df.columns]], ignore_index=True)


CANCERS = [
    {
        "cancer_type": "Ovarian cancer",
        "cbio_study_candidates": "ov_tcga_pan_can_atlas_2018;ov_tcga",
        "depmap_oncotree_codes": "HGSOC;OVT;OVARY",
        "pubmed_query_terms": "ovarian cancer[Title/Abstract] OR ovarian carcinoma[Title/Abstract] OR HGSOC[Title/Abstract]",
    },
    {
        "cancer_type": "Endometrial cancer",
        "cbio_study_candidates": "ucec_tcga_pan_can_atlas_2018;ucec_tcga",
        "depmap_oncotree_codes": "UCEC;USC;UCS",
        "pubmed_query_terms": "endometrial cancer[Title/Abstract] OR uterine corpus endometrial carcinoma[Title/Abstract] OR UCEC[Title/Abstract]",
    },
    {
        "cancer_type": "Bladder cancer",
        "cbio_study_candidates": "blca_tcga_pan_can_atlas_2018;blca_tcga",
        "depmap_oncotree_codes": "BLCA",
        "pubmed_query_terms": "bladder cancer[Title/Abstract] OR urothelial carcinoma[Title/Abstract] OR BLCA[Title/Abstract]",
    },
    {
        "cancer_type": "Kidney clear cell carcinoma",
        "cbio_study_candidates": "kirc_tcga_pan_can_atlas_2018;kirc_tcga",
        "depmap_oncotree_codes": "CCRCC;KIRC",
        "pubmed_query_terms": "clear cell renal cell carcinoma[Title/Abstract] OR kidney clear cell carcinoma[Title/Abstract] OR KIRC[Title/Abstract]",
    },
    {
        "cancer_type": "Kidney papillary carcinoma",
        "cbio_study_candidates": "kirp_tcga_pan_can_atlas_2018;kirp_tcga",
        "depmap_oncotree_codes": "PRCC;KIRP",
        "pubmed_query_terms": "papillary renal cell carcinoma[Title/Abstract] OR kidney papillary carcinoma[Title/Abstract] OR KIRP[Title/Abstract]",
    },
    {
        "cancer_type": "Liver cancer",
        "cbio_study_candidates": "lihc_tcga_pan_can_atlas_2018;lihc_tcga",
        "depmap_oncotree_codes": "HCC;LIHC",
        "pubmed_query_terms": "liver cancer[Title/Abstract] OR hepatocellular carcinoma[Title/Abstract] OR LIHC[Title/Abstract]",
    },
    {
        "cancer_type": "Thyroid cancer",
        "cbio_study_candidates": "thca_tcga_pan_can_atlas_2018;thca_tcga",
        "depmap_oncotree_codes": "THCA;PTC",
        "pubmed_query_terms": "thyroid cancer[Title/Abstract] OR thyroid carcinoma[Title/Abstract] OR THCA[Title/Abstract]",
    },
    {
        "cancer_type": "Head and neck cancer",
        "cbio_study_candidates": "hnsc_tcga_pan_can_atlas_2018;hnsc_tcga",
        "depmap_oncotree_codes": "HNSC;HNSCC",
        "pubmed_query_terms": "head and neck cancer[Title/Abstract] OR head and neck squamous cell carcinoma[Title/Abstract] OR HNSCC[Title/Abstract]",
    },
    {
        "cancer_type": "Esophageal cancer",
        "cbio_study_candidates": "esca_tcga_pan_can_atlas_2018;esca_tcga",
        "depmap_oncotree_codes": "ESCA;ESCC;EAC",
        "pubmed_query_terms": "esophageal cancer[Title/Abstract] OR esophageal carcinoma[Title/Abstract] OR ESCA[Title/Abstract]",
    },
    {
        "cancer_type": "Cervical cancer",
        "cbio_study_candidates": "cesc_tcga_pan_can_atlas_2018;cesc_tcga",
        "depmap_oncotree_codes": "CESC",
        "pubmed_query_terms": "cervical cancer[Title/Abstract] OR cervical carcinoma[Title/Abstract] OR CESC[Title/Abstract]",
    },
    {
        "cancer_type": "Lung squamous cell carcinoma",
        "cbio_study_candidates": "lusc_tcga_pan_can_atlas_2018;lusc_tcga",
        "depmap_oncotree_codes": "LUSC",
        "pubmed_query_terms": "lung squamous cell carcinoma[Title/Abstract] OR LUSC[Title/Abstract]",
    },
    {
        "cancer_type": "Low-grade glioma",
        "cbio_study_candidates": "lgg_tcga_pan_can_atlas_2018;lgg_tcga",
        "depmap_oncotree_codes": "LGG;ODG;ASTR",
        "pubmed_query_terms": "low-grade glioma[Title/Abstract] OR LGG[Title/Abstract] OR glioma[Title/Abstract]",
    },
    {
        "cancer_type": "Sarcoma",
        "cbio_study_candidates": "sarc_tcga_pan_can_atlas_2018;sarc_tcga",
        "depmap_oncotree_codes": "SARC;LIPO;LMS;UPS",
        "pubmed_query_terms": "sarcoma[Title/Abstract] OR soft tissue sarcoma[Title/Abstract] OR SARC[Title/Abstract]",
    },
    {
        "cancer_type": "Cholangiocarcinoma",
        "cbio_study_candidates": "chol_tcga_pan_can_atlas_2018;chol_tcga",
        "depmap_oncotree_codes": "CHOL;IHCH",
        "pubmed_query_terms": "cholangiocarcinoma[Title/Abstract] OR bile duct cancer[Title/Abstract] OR CHOL[Title/Abstract]",
    },
    {
        "cancer_type": "Adrenocortical carcinoma",
        "cbio_study_candidates": "acc_tcga_pan_can_atlas_2018;acc_tcga",
        "depmap_oncotree_codes": "ACC",
        "pubmed_query_terms": "adrenocortical carcinoma[Title/Abstract] OR adrenal cortical carcinoma[Title/Abstract] OR ACC[Title/Abstract]",
    },
    {
        "cancer_type": "Mesothelioma",
        "cbio_study_candidates": "meso_tcga_pan_can_atlas_2018;meso_tcga",
        "depmap_oncotree_codes": "MESO;PLMESO",
        "pubmed_query_terms": "mesothelioma[Title/Abstract] OR malignant pleural mesothelioma[Title/Abstract]",
    },
    {
        "cancer_type": "Uveal melanoma",
        "cbio_study_candidates": "uvm_tcga_pan_can_atlas_2018;uvm_tcga",
        "depmap_oncotree_codes": "UVM",
        "pubmed_query_terms": "uveal melanoma[Title/Abstract] OR ocular melanoma[Title/Abstract] OR UVM[Title/Abstract]",
    },
    {
        "cancer_type": "Testicular germ cell tumor",
        "cbio_study_candidates": "tgct_tcga_pan_can_atlas_2018;tgct_tcga",
        "depmap_oncotree_codes": "TGCT;NSGCT;SEMGCT",
        "pubmed_query_terms": "testicular germ cell tumor[Title/Abstract] OR TGCT[Title/Abstract]",
    },
    {
        "cancer_type": "Acute myeloid leukemia",
        "cbio_study_candidates": "laml_tcga_pan_can_atlas_2018;laml_tcga",
        "depmap_oncotree_codes": "AML;LAML",
        "pubmed_query_terms": "acute myeloid leukemia[Title/Abstract] OR AML[Title/Abstract] OR LAML[Title/Abstract]",
    },
    {
        "cancer_type": "Diffuse large B-cell lymphoma",
        "cbio_study_candidates": "dlbc_tcga_pan_can_atlas_2018;dlbc_tcga",
        "depmap_oncotree_codes": "DLBCL;DLBC",
        "pubmed_query_terms": "diffuse large B-cell lymphoma[Title/Abstract] OR DLBCL[Title/Abstract]",
    },
]


PAN_CANCER_CORE = [
    "TP53", "MYC", "KRAS", "NRAS", "HRAS", "BRAF", "EGFR", "ERBB2", "ERBB3", "MET",
    "PIK3CA", "PIK3R1", "PTEN", "AKT1", "MTOR", "APC", "CTNNB1", "SMAD4", "TGFBR2",
    "CDKN2A", "CDKN2B", "RB1", "CCND1", "CDK4", "CDK6", "MDM2", "MDM4",
    "BRCA1", "BRCA2", "ATM", "ATR", "CHEK1", "CHEK2", "PALB2", "RAD51", "MSH2", "MSH6", "MLH1", "PMS2",
    "TERT", "ARID1A", "ARID1B", "SMARCA4", "SMARCB1", "KMT2D", "KMT2C", "CREBBP", "EP300",
    "NOTCH1", "NOTCH2", "FBXW7", "NFE2L2", "KEAP1", "HIF1A", "VEGFA",
    "CD274", "PDCD1LG2", "JAK1", "JAK2", "B2M",
    "EPCAM", "MUC1", "MUC16", "MSLN", "CLDN18", "CD276", "TROP2", "NECTIN4",
]

CANCER_SPECIFIC = {
    "GBM": ["OIP5", "MGMT", "IDH1", "IDH2", "ATRX", "PDGFRA", "OLIG2", "SOX2", "NES", "PROM1", "IL13RA2", "EPHA2"],
    "Gastric cancer": ["ERBB2", "FGFR2", "CLDN18", "CDH1", "MET", "KRAS", "MSLN", "MUC1", "MUC16", "EPCAM"],
    "Breast cancer": ["ESR1", "PGR", "GATA3", "FOXA1", "ERBB2", "PIK3CA", "BRCA1", "BRCA2", "CCND1"],
    "Lung adenocarcinoma": ["EGFR", "ALK", "ROS1", "RET", "MET", "BRAF", "KRAS", "ERBB2", "NTRK1"],
    "Colorectal cancer": ["APC", "KRAS", "BRAF", "SMAD4", "MSH2", "MSH6", "MLH1", "ERBB2", "TGFBR2"],
    "Pancreatic cancer": ["KRAS", "TP53", "CDKN2A", "SMAD4", "BRCA1", "BRCA2", "MSLN", "ERBB2"],
    "Melanoma": ["BRAF", "NRAS", "NF1", "KIT", "MITF", "TERT", "CDKN2A", "PTEN"],
    "Prostate cancer": ["AR", "FOXA1", "SPOP", "PTEN", "ERG", "TMPRSS2", "BRCA1", "BRCA2"],
    "Ovarian cancer": ["BRCA1", "BRCA2", "TP53", "CCNE1", "NF1", "RB1", "RAD51C", "RAD51D", "MUC16", "FOLR1"],
    "Endometrial cancer": ["PTEN", "PIK3CA", "ARID1A", "CTNNB1", "KRAS", "POLE", "PPP2R1A", "TP53", "FGFR2"],
    "Bladder cancer": ["FGFR3", "TERT", "KDM6A", "ARID1A", "ERBB2", "ERBB3", "RB1", "TP53", "PPARG", "NECTIN4"],
    "Kidney clear cell carcinoma": ["VHL", "PBRM1", "SETD2", "BAP1", "MTOR", "PTEN", "KDM5C", "VEGFA", "HIF1A"],
    "Kidney papillary carcinoma": ["MET", "FH", "SETD2", "NF2", "CDKN2A", "TERT", "BAP1", "MTOR"],
    "Liver cancer": ["TERT", "CTNNB1", "TP53", "AXIN1", "ARID1A", "NFE2L2", "KEAP1", "VEGFA", "FGF19"],
    "Thyroid cancer": ["BRAF", "RET", "NTRK1", "NTRK3", "RAS", "NRAS", "HRAS", "TERT", "EIF1AX"],
    "Head and neck cancer": ["TP53", "CDKN2A", "PIK3CA", "NOTCH1", "FAT1", "CASP8", "HRAS", "EGFR", "CCND1"],
    "Esophageal cancer": ["TP53", "ERBB2", "EGFR", "CCND1", "CDKN2A", "SMAD4", "NOTCH1", "NFE2L2"],
    "Cervical cancer": ["PIK3CA", "PTEN", "KRAS", "ERBB2", "FBXW7", "HLA-A", "B2M", "CD274"],
    "Lung squamous cell carcinoma": ["TP53", "CDKN2A", "SOX2", "PIK3CA", "NFE2L2", "KEAP1", "FGFR1", "DDR2", "EGFR"],
    "Low-grade glioma": ["IDH1", "IDH2", "ATRX", "TP53", "CIC", "FUBP1", "TERT", "BRAF", "FGFR1"],
    "Sarcoma": ["MDM2", "CDK4", "TP53", "RB1", "ATRX", "KIT", "PDGFRA", "NTRK1", "SS18"],
    "Cholangiocarcinoma": ["IDH1", "IDH2", "FGFR2", "BAP1", "ARID1A", "KRAS", "TP53", "ERBB2", "MET"],
    "Adrenocortical carcinoma": ["TP53", "CTNNB1", "ZNRF3", "MEN1", "PRKAR1A", "TERT", "IGF2"],
    "Mesothelioma": ["BAP1", "NF2", "CDKN2A", "SETD2", "TP53", "LATS2", "MSLN"],
    "Uveal melanoma": ["GNAQ", "GNA11", "BAP1", "SF3B1", "EIF1AX", "CYSLTR2", "PLCB4"],
    "Testicular germ cell tumor": ["KIT", "KRAS", "NRAS", "BRAF", "MDM2", "CCND2", "TP53"],
    "Acute myeloid leukemia": ["FLT3", "NPM1", "DNMT3A", "IDH1", "IDH2", "TET2", "RUNX1", "CEBPA", "KIT", "TP53"],
    "Diffuse large B-cell lymphoma": ["MYD88", "CD79B", "BCL2", "BCL6", "MYC", "EZH2", "CREBBP", "KMT2D", "TP53", "CD19"],
}

GENE_META = {
    "TP53": ("Tumor suppressor", "p53 pathway regulator", "DNA damage response / cell-cycle checkpoint", "Tumor-suppressor pathway"),
    "MYC": ("Oncogene", "Transcription factor", "Proliferation and growth control", "MYC/proliferation program"),
    "KRAS": ("Oncogene", "Small GTPase", "RAS-MAPK signaling", "RAS-MAPK signaling"),
    "NRAS": ("Oncogene", "Small GTPase", "RAS-MAPK signaling", "RAS-MAPK signaling"),
    "HRAS": ("Oncogene", "Small GTPase", "RAS-MAPK signaling", "RAS-MAPK signaling"),
    "BRAF": ("Oncogene", "Serine/threonine kinase", "MAPK signaling", "MAPK signaling"),
    "EGFR": ("Oncogene", "Receptor tyrosine kinase", "RTK signaling", "RTK signaling"),
    "ERBB2": ("Oncogene", "Receptor tyrosine kinase", "HER2/RTK signaling", "RTK signaling"),
    "ERBB3": ("Oncogene / pathway receptor", "Receptor tyrosine kinase family member", "HER/PI3K signaling", "RTK signaling"),
    "MET": ("Oncogene", "Receptor tyrosine kinase", "HGF-MET signaling", "RTK signaling"),
    "ALK": ("Oncogenic fusion kinase", "Receptor tyrosine kinase", "Fusion-driven RTK signaling", "RTK / fusion signaling"),
    "ROS1": ("Oncogenic fusion kinase", "Receptor tyrosine kinase", "Fusion-driven RTK signaling", "RTK / fusion signaling"),
    "RET": ("Oncogenic fusion kinase", "Receptor tyrosine kinase", "RET signaling", "RTK / fusion signaling"),
    "NTRK1": ("Oncogenic fusion kinase", "Receptor tyrosine kinase", "TRK signaling", "RTK / fusion signaling"),
    "NTRK3": ("Oncogenic fusion kinase", "Receptor tyrosine kinase", "TRK signaling", "RTK / fusion signaling"),
    "FGFR1": ("Oncogene / pathway receptor", "Receptor tyrosine kinase", "FGF signaling", "RTK signaling"),
    "FGFR2": ("Oncogene / pathway receptor", "Receptor tyrosine kinase", "FGF signaling", "RTK signaling"),
    "FGFR3": ("Oncogene / pathway receptor", "Receptor tyrosine kinase", "FGF signaling", "RTK signaling"),
    "PIK3CA": ("Oncogene", "PI3K catalytic subunit", "PI3K-AKT signaling", "PI3K-AKT signaling"),
    "PIK3R1": ("Pathway regulator", "PI3K regulatory subunit", "PI3K-AKT signaling", "PI3K-AKT signaling"),
    "PTEN": ("Tumor suppressor", "Lipid phosphatase", "PI3K pathway restraint", "PI3K-AKT signaling"),
    "AKT1": ("Oncogene / signaling kinase", "Serine/threonine kinase", "AKT signaling", "PI3K-AKT signaling"),
    "MTOR": ("Growth signaling regulator", "Serine/threonine kinase", "mTOR signaling", "PI3K-AKT-mTOR signaling"),
    "APC": ("Tumor suppressor", "WNT destruction-complex regulator", "WNT signaling", "WNT signaling"),
    "CTNNB1": ("Oncogene / pathway effector", "Beta-catenin", "WNT signaling", "WNT signaling"),
    "SMAD4": ("Tumor suppressor", "TGF-beta pathway mediator", "TGF-beta signaling", "TGF-beta signaling"),
    "TGFBR2": ("Tumor suppressor / pathway receptor", "TGF-beta receptor", "TGF-beta signaling", "TGF-beta signaling"),
    "CDKN2A": ("Tumor suppressor", "Cell-cycle inhibitor locus", "CDK4/6-RB control", "Cell cycle"),
    "CDKN2B": ("Tumor suppressor", "Cell-cycle inhibitor locus", "CDK4/6-RB control", "Cell cycle"),
    "RB1": ("Tumor suppressor", "Cell-cycle checkpoint regulator", "G1/S cell-cycle control", "Cell cycle"),
    "CCND1": ("Oncogene / cell-cycle regulator", "Cyclin", "CDK4/6-RB control", "Cell cycle"),
    "CCND2": ("Oncogene / cell-cycle regulator", "Cyclin", "CDK4/6-RB control", "Cell cycle"),
    "CDK4": ("Oncogene / cell-cycle kinase", "Cyclin-dependent kinase", "CDK4/6-RB control", "Cell cycle"),
    "CDK6": ("Oncogene / cell-cycle kinase", "Cyclin-dependent kinase", "CDK4/6-RB control", "Cell cycle"),
    "MDM2": ("Oncogene / p53 regulator", "E3 ubiquitin ligase", "p53 suppression", "p53 pathway"),
    "MDM4": ("Oncogene / p53 regulator", "p53 pathway inhibitor", "p53 suppression", "p53 pathway"),
    "BRCA1": ("DNA repair tumor suppressor", "Homologous recombination repair gene", "DNA double-strand break repair", "DNA repair / HRD"),
    "BRCA2": ("DNA repair tumor suppressor", "Homologous recombination repair gene", "DNA double-strand break repair", "DNA repair / HRD"),
    "ATM": ("DNA damage response tumor suppressor", "DNA damage response kinase", "DNA repair checkpoint signaling", "DNA damage response"),
    "ATR": ("DNA damage response kinase", "Replication stress response kinase", "DNA replication stress response", "DNA damage response"),
    "CHEK1": ("DNA damage response kinase", "Checkpoint kinase", "Replication stress checkpoint", "DNA damage response"),
    "CHEK2": ("DNA damage response tumor suppressor", "Checkpoint kinase", "DNA damage checkpoint", "DNA damage response"),
    "PALB2": ("DNA repair tumor suppressor", "Homologous recombination repair gene", "DNA repair", "DNA repair / HRD"),
    "RAD51": ("DNA repair factor", "Homologous recombination factor", "DNA repair", "DNA repair / HRD"),
    "MSH2": ("DNA repair tumor suppressor", "Mismatch repair gene", "Mismatch repair / MSI", "Mismatch repair / MSI"),
    "MSH6": ("DNA repair tumor suppressor", "Mismatch repair gene", "Mismatch repair / MSI", "Mismatch repair / MSI"),
    "MLH1": ("DNA repair tumor suppressor", "Mismatch repair gene", "Mismatch repair / MSI", "Mismatch repair / MSI"),
    "PMS2": ("DNA repair tumor suppressor", "Mismatch repair gene", "Mismatch repair / MSI", "Mismatch repair / MSI"),
    "TERT": ("Cancer-associated maintenance gene", "Telomerase catalytic subunit", "Telomere maintenance", "Telomere maintenance"),
    "ARID1A": ("Chromatin regulator / tumor suppressor", "SWI/SNF chromatin regulator", "Chromatin remodeling", "Chromatin remodeling"),
    "ARID1B": ("Chromatin regulator / tumor suppressor", "SWI/SNF chromatin regulator", "Chromatin remodeling", "Chromatin remodeling"),
    "SMARCA4": ("Chromatin regulator / tumor suppressor", "SWI/SNF ATPase", "Chromatin remodeling", "Chromatin remodeling"),
    "SMARCB1": ("Chromatin regulator / tumor suppressor", "SWI/SNF component", "Chromatin remodeling", "Chromatin remodeling"),
    "KMT2D": ("Epigenetic regulator", "Histone methyltransferase", "Chromatin regulation", "Epigenetic regulation"),
    "KMT2C": ("Epigenetic regulator", "Histone methyltransferase", "Chromatin regulation", "Epigenetic regulation"),
    "CREBBP": ("Epigenetic regulator", "Histone acetyltransferase", "Chromatin regulation", "Epigenetic regulation"),
    "EP300": ("Epigenetic regulator", "Histone acetyltransferase", "Chromatin regulation", "Epigenetic regulation"),
    "NOTCH1": ("Oncogene / tumor suppressor context-dependent", "Notch receptor", "Notch signaling", "Notch signaling"),
    "NOTCH2": ("Oncogene / pathway receptor", "Notch receptor", "Notch signaling", "Notch signaling"),
    "FBXW7": ("Tumor suppressor / protein turnover regulator", "E3 ubiquitin ligase component", "Protein turnover", "Protein turnover"),
    "NFE2L2": ("Stress-response oncogene", "Transcription factor", "Oxidative stress response", "Oxidative stress / NRF2"),
    "KEAP1": ("Tumor suppressor / stress pathway regulator", "NRF2 pathway repressor", "Oxidative stress response", "Oxidative stress / NRF2"),
    "HIF1A": ("Hypoxia pathway regulator", "Transcription factor", "Hypoxia response", "Hypoxia / angiogenesis"),
    "VEGFA": ("Microenvironment / angiogenesis factor", "Secreted ligand", "Angiogenesis", "Angiogenesis / microenvironment"),
    "CD274": ("Immune checkpoint ligand", "Immune checkpoint ligand", "Tumor immune evasion", "Immune checkpoint"),
    "PDCD1LG2": ("Immune checkpoint ligand", "Immune checkpoint ligand", "Tumor immune evasion", "Immune checkpoint"),
    "JAK1": ("Immune signaling kinase", "Tyrosine kinase", "Interferon/JAK-STAT signaling", "JAK-STAT / immune signaling"),
    "JAK2": ("Immune signaling kinase", "Tyrosine kinase", "JAK-STAT signaling", "JAK-STAT / immune signaling"),
    "B2M": ("Immune antigen-presentation gene", "MHC class I component", "Antigen presentation", "Antigen presentation"),
    "EPCAM": ("Epithelial surface antigen", "Cell adhesion / surface antigen", "Epithelial identity", "Epithelial antigen / adhesion"),
    "MUC1": ("Tumor-associated surface antigen", "Mucin / surface glycoprotein", "Epithelial tumor antigen context", "Epithelial antigen / mucin biology"),
    "MUC16": ("Tumor-associated surface antigen", "Mucin / surface glycoprotein", "Tumor antigen context", "Epithelial antigen / mucin biology"),
    "MSLN": ("Tumor-associated surface antigen", "Cell-surface antigen", "Tumor antigen context", "Tumor antigen / adhesion"),
    "CLDN18": ("Tumor-associated surface antigen", "Tight-junction / surface antigen", "Epithelial lineage antigen context", "Epithelial antigen / tight junction"),
    "CD276": ("Immune/tumor-associated surface antigen", "Immune checkpoint / surface antigen", "Tumor immune interaction", "Immune checkpoint / tumor antigen"),
    "TROP2": ("Tumor-associated surface antigen", "Surface glycoprotein", "Epithelial tumor antigen context", "Tumor antigen"),
    "NECTIN4": ("Tumor-associated surface antigen", "Cell adhesion / surface antigen", "Epithelial tumor antigen context", "Tumor antigen"),
    "VHL": ("Tumor suppressor", "Hypoxia pathway regulator", "HIF/oxygen sensing", "Hypoxia / angiogenesis"),
    "PBRM1": ("Chromatin regulator / tumor suppressor", "SWI/SNF chromatin regulator", "Chromatin remodeling", "Chromatin remodeling"),
    "SETD2": ("Epigenetic regulator / tumor suppressor", "Histone methyltransferase", "Chromatin regulation / DNA repair", "Epigenetic regulation"),
    "BAP1": ("Tumor suppressor / chromatin regulator", "Deubiquitinase", "Chromatin regulation and DNA repair", "Chromatin / DNA repair"),
    "IDH1": ("Metabolic oncogene", "Metabolic enzyme", "Oncometabolite production", "Metabolism / epigenetic state"),
    "IDH2": ("Metabolic oncogene", "Metabolic enzyme", "Oncometabolite production", "Metabolism / epigenetic state"),
    "FLT3": ("Oncogene", "Receptor tyrosine kinase", "FLT3 signaling", "RTK signaling"),
    "NPM1": ("Leukemia-associated gene", "Nucleolar protein", "AML subtype biology", "Leukemia subtype biology"),
    "DNMT3A": ("Epigenetic regulator / tumor suppressor", "DNA methyltransferase", "DNA methylation", "Epigenetic regulation"),
    "TET2": ("Epigenetic regulator / tumor suppressor", "DNA demethylation regulator", "DNA methylation state", "Epigenetic regulation"),
    "RUNX1": ("Lineage transcription factor / tumor suppressor", "Transcription factor", "Hematopoietic differentiation", "Hematopoietic lineage state"),
    "CEBPA": ("Lineage transcription factor", "Transcription factor", "Myeloid differentiation", "Hematopoietic lineage state"),
    "MYD88": ("Immune signaling adaptor oncogene", "Signaling adaptor", "NF-kB signaling", "NF-kB / immune signaling"),
    "CD79B": ("B-cell receptor pathway gene", "BCR component", "B-cell receptor signaling", "BCR signaling"),
    "BCL2": ("Apoptosis regulator oncogene", "Anti-apoptotic protein", "Apoptosis suppression", "Apoptosis"),
    "BCL6": ("Lineage transcription factor oncogene", "Transcriptional repressor", "B-cell state regulation", "B-cell lineage state"),
    "EZH2": ("Epigenetic regulator oncogene", "Histone methyltransferase", "Polycomb repression", "Epigenetic regulation"),
    "CD19": ("B-cell surface antigen", "Surface antigen", "B-cell antigen context", "Tumor antigen"),
    "AR": ("Lineage/onco-dependency transcription factor", "Nuclear hormone receptor", "Androgen receptor signaling", "Hormone receptor signaling"),
    "ESR1": ("Lineage/onco-dependency transcription factor", "Nuclear hormone receptor", "Estrogen receptor signaling", "Hormone receptor signaling"),
    "PGR": ("Hormone receptor biomarker", "Nuclear hormone receptor", "Progesterone receptor signaling", "Hormone receptor signaling"),
    "GATA3": ("Lineage transcription factor", "Transcription factor", "Breast/luminal lineage state", "Lineage transcriptional state"),
    "FOXA1": ("Lineage transcription factor", "Pioneer transcription factor", "Hormone receptor chromatin program", "Lineage chromatin regulation"),
    "MITF": ("Lineage transcription factor", "Transcription factor", "Melanocyte lineage state", "Lineage transcriptional state"),
    "FOLR1": ("Tumor-associated surface antigen", "Surface receptor", "Folate receptor antigen context", "Tumor antigen"),
}

HIGH_THERAPEUTIC_GENES = {
    "ERBB2", "EGFR", "ALK", "ROS1", "RET", "NTRK1", "NTRK3", "BRAF", "MET", "FGFR2", "FGFR3",
    "ESR1", "AR", "BRCA1", "BRCA2", "MSH2", "MSH6", "MLH1", "PMS2", "FLT3", "IDH1", "IDH2",
    "CD19", "BCL2", "EZH2", "CD274", "MSLN", "CLDN18", "FOLR1", "NECTIN4", "TROP2",
}


def role_for_gene(gene):
    if gene in GENE_META:
        category, target, process, pathway = GENE_META[gene]
        return {
            "gene": gene,
            "role_category": category,
            "target_class": target,
            "biological_process": process,
            "interpretation_note": f"{gene} should be interpreted through {process} context; do not infer therapeutic actionability from one evidence layer alone.",
        }

    return {
        "gene": gene,
        "role_category": "Cancer-associated gene",
        "target_class": "Curated cancer-context gene",
        "biological_process": "Cancer-associated biology",
        "interpretation_note": f"{gene} is included as a curated cancer-context gene; interpretation requires layer-specific validation.",
    }


def pathway_for_gene(gene):
    if gene in GENE_META:
        category, target, process, pathway = GENE_META[gene]
        return {
            "gene": gene,
            "pathway_category": pathway,
            "function_group": target,
            "pathway_process": process,
            "interpretive_use": f"Use {gene} as {pathway} context rather than a standalone claim.",
            "validation_suggestions": f"Check alteration, expression, dependency, subgroup specificity, and literature support for {gene}.",
        }

    return {
        "gene": gene,
        "pathway_category": "Cancer-associated pathway context",
        "function_group": "Curated cancer-context gene",
        "pathway_process": "Cancer-associated biology",
        "interpretive_use": f"Use {gene} as a hypothesis-generating cancer-context gene.",
        "validation_suggestions": f"Check alteration, expression, dependency, subgroup specificity, and literature support for {gene}.",
    }


def therapeutic_for_pair(gene, cancer_type):
    if gene == "ERBB2" and cancer_type == "Gastric cancer":
        return {
            "gene": gene,
            "cancer_type": cancer_type,
            "therapeutic_relevance": "High therapeutic relevance",
            "therapeutic_context": "HER2-directed therapeutic biomarker context in gastric/GEJ adenocarcinoma",
            "biomarker_type": "Amplification/overexpression biomarker",
            "dependency_interpretation": "Do not interpret weak DepMap dependency as absence of clinical relevance.",
            "therapeutic_caution": "Therapeutic relevance is subgroup-specific and requires amplification/expression/protein-level validation.",
            "validation_suggestions": "Check HER2 amplification-expression concordance, protein/IHC or FISH evidence, subgroup-specific pathway activity, and therapy-response literature.",
        }

    if gene in HIGH_THERAPEUTIC_GENES:
        relevance = "High therapeutic/biomarker relevance"
        biomarker_type = "Therapeutic or biomarker-context gene"
        caution = "Requires cancer-specific biomarker framing and validation."
    elif any(token in role_for_gene(gene)["role_category"].lower() for token in ["surface antigen", "immune checkpoint"]):
        relevance = "Antigen/immune biomarker relevance"
        biomarker_type = "Surface antigen or immune biomarker"
        caution = "Requires protein-level expression, tumor-normal safety, and heterogeneity validation."
    elif any(token in pathway_for_gene(gene)["pathway_category"].lower() for token in ["dna repair", "mismatch repair", "hormone", "rtk", "mapk", "pi3k"]):
        relevance = "Pathway-context relevance"
        biomarker_type = "Pathway or alteration-context biomarker"
        caution = "Requires alteration/subgroup-specific interpretation."
    else:
        relevance = "Research-context relevance"
        biomarker_type = "Research-use hypothesis gene"
        caution = "Do not interpret as clinical actionability."

    return {
        "gene": gene,
        "cancer_type": cancer_type,
        "therapeutic_relevance": relevance,
        "therapeutic_context": f"{gene} in {cancer_type} research/biomarker context",
        "biomarker_type": biomarker_type,
        "dependency_interpretation": "DepMap dependency and biomarker relevance should be interpreted as separate evidence layers.",
        "therapeutic_caution": caution,
        "validation_suggestions": f"Validate {gene} in {cancer_type} using alteration, expression, patient subgroup, dependency, and literature evidence.",
    }


def mock_pair(gene, cancer_type):
    role = role_for_gene(gene)["role_category"]
    pathway = pathway_for_gene(gene)["pathway_category"]

    if any(x in role.lower() for x in ["surface antigen", "immune checkpoint"]):
        dep = "Not primary dependency mechanism"
        safety = "Tumor-normal expression safety required"
        mut = "Expression/antigen context"
    elif any(x in role.lower() for x in ["tumor suppressor", "dna repair"]):
        dep = "Variable"
        safety = "Loss-of-function context"
        mut = "Alteration/loss context"
    elif any(x in role.lower() for x in ["oncogene", "kinase", "receptor"]):
        dep = "Variable"
        safety = "Pathway/subgroup safety context"
        mut = "Alteration/pathway context"
    else:
        dep = "Variable"
        safety = "Context-dependent safety"
        mut = "Known cancer-context gene"

    return {
        "gene": gene,
        "cancer_type": cancer_type,
        "tumor_expression": "Context-dependent",
        "survival_association": "Unclear",
        "geo_validation": "Needs validation",
        "depmap_dependency": dep,
        "normal_tissue_safety": safety,
        "mutation_cna_support": mut,
        "novelty_score": 5,
        "notes": f"Pan-cancer catalog hypothesis: {gene} in {cancer_type}; pathway context: {pathway}.",
    }


def main():
    registry_df = pd.read_csv(REGISTRY_PATH)
    mock_df = pd.read_csv(MOCK_PATH)
    role_df = pd.read_csv(ROLE_PATH)
    pathway_df = pd.read_csv(PATHWAY_PATH)
    ther_df = pd.read_csv(THER_PATH)

    registry_df = upsert(registry_df, CANCERS, ["cancer_type"])

    all_existing_cancers = sorted(set(registry_df["cancer_type"].astype(str)))

    pair_rows = []
    for cancer in all_existing_cancers:
        genes = set(PAN_CANCER_CORE)
        genes.update(CANCER_SPECIFIC.get(cancer, []))
        for gene in sorted(genes):
            pair_rows.append(mock_pair(gene, cancer))

    all_genes = sorted({row["gene"] for row in pair_rows})
    role_rows = [role_for_gene(g) for g in all_genes]
    pathway_rows = [pathway_for_gene(g) for g in all_genes]
    therapeutic_rows = [therapeutic_for_pair(row["gene"], row["cancer_type"]) for row in pair_rows]

    mock_df = upsert(mock_df, pair_rows, ["gene", "cancer_type"])
    role_df = upsert(role_df, role_rows, ["gene"])
    pathway_df = upsert(pathway_df, pathway_rows, ["gene"])
    ther_df = upsert(ther_df, therapeutic_rows, ["gene", "cancer_type"])

    registry_df.to_csv(REGISTRY_PATH, index=False)
    mock_df.to_csv(MOCK_PATH, index=False)
    role_df.to_csv(ROLE_PATH, index=False)
    pathway_df.to_csv(PATHWAY_PATH, index=False)
    ther_df.to_csv(THER_PATH, index=False)

    print("Pan-cancer catalog expansion complete.")
    print("Cancer types:", registry_df["cancer_type"].nunique())
    print("Gene-cancer pairs:", len(mock_df.drop_duplicates(["gene", "cancer_type"])))
    print("Unique genes:", mock_df["gene"].nunique())
    print()
    print(mock_df.groupby("cancer_type")["gene"].nunique().sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()