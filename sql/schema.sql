CREATE TABLE IF NOT EXISTS companies (
  id INT AUTO_INCREMENT PRIMARY KEY,
  stock_id VARCHAR(10) NOT NULL UNIQUE COMMENT '有價證券代號',
  name VARCHAR(255) NOT NULL COMMENT '公司名稱',
  isin_code VARCHAR(20) COMMENT '國際證券辨識號碼(ISIN)',
  listing_date DATE COMMENT '上市日',
  market_type VARCHAR(50) COMMENT '市場別',
  industry VARCHAR(100) COMMENT '產業別',
  cfi_code VARCHAR(20) COMMENT 'CFICode',
  is_listed BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS financial_statements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  stock_id VARCHAR(10) NOT NULL,
  year INT NOT NULL,
  season ENUM('Q1', 'Q2', 'Q3', 'Q4') NOT NULL,
  statement_type ENUM('income', 'balance_sheet', 'cash_flow') NOT NULL,
  account_code VARCHAR(20) DEFAULT NULL COMMENT '會計科目代號',
  item_name VARCHAR(255) NOT NULL COMMENT '報表上的項目名稱',
  value BIGINT DEFAULT NULL COMMENT '數值（元）',
  unit VARCHAR(20) DEFAULT 'NTD' COMMENT '數字單位（新台幣元、新台幣仟元等）',

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY unique_statement (stock_id, year, season, statement_type, item_name)
);