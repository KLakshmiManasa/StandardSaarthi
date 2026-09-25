-- Database Schema for SIH 26108: AI-Powered Indian Standards Recommendation Engine
-- PostgreSQL 15+ Schema DDL Foundation

DROP TABLE IF EXISTS standard_relationships CASCADE;
DROP TABLE IF EXISTS qco_compliance CASCADE;
DROP TABLE IF EXISTS procurement_queries CASCADE;
DROP TABLE IF EXISTS standards_master CASCADE;

-- 1. STANDARDS MASTER TABLE
CREATE TABLE standards_master (
    is_code VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    edition_year INT CHECK (edition_year IS NULL OR (edition_year >= 1900 AND edition_year <= 2026)),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUPERSEDED', 'WITHDRAWN', 'UNKNOWN')),
    sector VARCHAR(100) NOT NULL CHECK (sector IN ('Electrical', 'Civil', 'Mechanical', 'Electronics', 'General')),
    product_category VARCHAR(150) NOT NULL,
    scope_text TEXT NOT NULL,
    keywords TEXT,
    materials TEXT,
    applications TEXT,
    technical_parameters TEXT,
    test_methods TEXT,
    normative_references TEXT,
    installation_references TEXT,
    amendments TEXT,
    certification_information TEXT,
    qco_applicability VARCHAR(20) NOT NULL DEFAULT 'UNKNOWN' CHECK (qco_applicability IN ('MANDATORY', 'NOT_MANDATORY', 'UNKNOWN')),
    source_url TEXT,
    source_document TEXT,
    source_type VARCHAR(30) NOT NULL DEFAULT 'CURATED_PILOT' CHECK (source_type IN ('PRIMARY_OFFICIAL', 'SECONDARY_GOVT', 'CURATED_PILOT')),
    last_verified_date DATE NOT NULL DEFAULT CURRENT_DATE,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'VERIFIED' CHECK (verification_status IN ('VERIFIED', 'NEEDS_REVIEW'))
);

-- Indexes for Fast Keyword and Metadata Search
CREATE INDEX idx_standards_sector ON standards_master(sector);
CREATE INDEX idx_standards_status ON standards_master(status);
CREATE INDEX idx_standards_qco ON standards_master(qco_applicability);

-- Full-Text Search Vector Index for BM25 / Lexical Matching
ALTER TABLE standards_master ADD COLUMN search_vector tsvector;
UPDATE standards_master SET search_vector = to_tsvector('english', coalesce(is_code, '') || ' ' || coalesce(title, '') || ' ' || coalesce(scope_text, '') || ' ' || coalesce(keywords, ''));
CREATE INDEX idx_standards_search ON standards_master USING gin(search_vector);

-- 2. STANDARDS RELATIONSHIPS TABLE
CREATE TABLE standard_relationships (
    relationship_id VARCHAR(50) PRIMARY KEY,
    source_is_code VARCHAR(50) NOT NULL REFERENCES standards_master(is_code) ON DELETE CASCADE,
    target_is_code VARCHAR(50) NOT NULL REFERENCES standards_master(is_code) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN ('NORMATIVE_REFERENCE', 'TEST_METHOD', 'MATERIAL_SPECIFICATION', 'INSTALLATION_CODE', 'RELATED_STANDARD', 'SUPERSEDES', 'AMENDED_BY')),
    description TEXT,
    source TEXT NOT NULL,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'VERIFIED' CHECK (verification_status IN ('VERIFIED', 'NEEDS_REVIEW')),
    CONSTRAINT unique_rel UNIQUE (source_is_code, target_is_code, relationship_type)
);

CREATE INDEX idx_rel_source ON standard_relationships(source_is_code);
CREATE INDEX idx_rel_target ON standard_relationships(target_is_code);
CREATE INDEX idx_rel_type ON standard_relationships(relationship_type);

-- 3. QCO COMPLIANCE TABLE
CREATE TABLE qco_compliance (
    qco_id VARCHAR(50) PRIMARY KEY,
    is_code VARCHAR(50) NOT NULL REFERENCES standards_master(is_code) ON DELETE CASCADE,
    qco_title TEXT NOT NULL,
    issuing_ministry VARCHAR(200) NOT NULL,
    notification_number VARCHAR(100) NOT NULL,
    notification_date DATE,
    mandatory_status VARCHAR(20) NOT NULL DEFAULT 'MANDATORY' CHECK (mandatory_status IN ('MANDATORY', 'NOT_MANDATORY', 'UNKNOWN')),
    effective_date DATE,
    source_url TEXT,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'VERIFIED' CHECK (verification_status IN ('VERIFIED', 'NEEDS_REVIEW')),
    last_verified_date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_qco_is_code ON qco_compliance(is_code);
CREATE INDEX idx_qco_ministry ON qco_compliance(issuing_ministry);

-- 4. PROCUREMENT QUERIES & GROUND TRUTH TABLE
CREATE TABLE procurement_queries (
    query_id VARCHAR(50) PRIMARY KEY,
    procurement_description TEXT NOT NULL,
    sector VARCHAR(100) NOT NULL,
    product TEXT,
    material TEXT,
    application TEXT,
    technical_requirements TEXT,
    environment TEXT,
    target_is_code VARCHAR(50) NOT NULL REFERENCES standards_master(is_code),
    related_is_codes TEXT,
    difficulty VARCHAR(20) NOT NULL DEFAULT 'MEDIUM' CHECK (difficulty IN ('EASY', 'MEDIUM', 'HARD')),
    source_type VARCHAR(30) NOT NULL DEFAULT 'MANUAL_VERIFIED' CHECK (source_type IN ('MANUAL_VERIFIED', 'SYNTHETIC')),
    verification_status VARCHAR(20) NOT NULL DEFAULT 'VERIFIED' CHECK (verification_status IN ('VERIFIED', 'NEEDS_REVIEW'))
);

CREATE INDEX idx_queries_target ON procurement_queries(target_is_code);
CREATE INDEX idx_queries_sector ON procurement_queries(sector);
CREATE INDEX idx_queries_difficulty ON procurement_queries(difficulty);
