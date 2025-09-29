#!/usr/bin/env python3
"""
Comprehensive database schema validation script
Analyzes current Azure database structure and compares with backend models
"""

import psycopg2
import sys
from typing import Dict, List, Any

def analyze_database_schema():
    """Analyze the current database schema in detail"""

    try:
        # Connection string for Azure PostgreSQL
        conn_string = "postgresql://aadaadmin:Universe1111@aada-pg-server27841.postgres.database.azure.com:5432/aada_local?sslmode=require"

        print("🔌 Connecting to Azure PostgreSQL database...")
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()

        print("✅ Connection successful!")
        print("\n" + "="*80)

        # Get detailed table structure
        cursor.execute("""
            SELECT
                t.table_name,
                c.column_name,
                c.data_type,
                c.character_maximum_length,
                c.is_nullable,
                c.column_default,
                tc.constraint_type,
                ccu.table_name AS referenced_table_name,
                ccu.column_name AS referenced_column_name
            FROM information_schema.tables t
            LEFT JOIN information_schema.columns c ON c.table_name = t.table_name
            LEFT JOIN information_schema.key_column_usage kcu ON kcu.table_name = t.table_name AND kcu.column_name = c.column_name
            LEFT JOIN information_schema.table_constraints tc ON tc.constraint_name = kcu.constraint_name AND tc.table_name = t.table_name
            LEFT JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
            WHERE t.table_schema = 'public'
            AND t.table_type = 'BASE TABLE'
            ORDER BY t.table_name, c.ordinal_position;
        """)

        schema_data = cursor.fetchall()

        # Organize data by table
        tables = {}
        for row in schema_data:
            table_name = row[0]
            if table_name not in tables:
                tables[table_name] = []

            column_info = {
                'column_name': row[1],
                'data_type': row[2],
                'max_length': row[3],
                'nullable': row[4],
                'default': row[5],
                'constraint_type': row[6],
                'references_table': row[7],
                'references_column': row[8]
            }
            tables[table_name].append(column_info)

        # Print detailed schema
        print("📊 DETAILED DATABASE SCHEMA ANALYSIS")
        print("="*80)

        for table_name, columns in tables.items():
            print(f"\n🗂️  TABLE: {table_name.upper()}")
            print("-" * 60)

            for col in columns:
                nullable = "NULL" if col['nullable'] == 'YES' else "NOT NULL"
                data_type = col['data_type']
                if col['max_length']:
                    data_type += f"({col['max_length']})"

                constraint_info = ""
                if col['constraint_type'] == 'PRIMARY KEY':
                    constraint_info = " 🔑 PRIMARY KEY"
                elif col['constraint_type'] == 'FOREIGN KEY':
                    ref = f"{col['references_table']}.{col['references_column']}"
                    constraint_info = f" 🔗 FK -> {ref}"

                default_info = ""
                if col['default']:
                    default_info = f" DEFAULT {col['default']}"

                print(f"   {col['column_name']:<25} {data_type:<20} {nullable:<10}{constraint_info}{default_info}")

        # Check for indexes
        print(f"\n\n🔍 INDEXES ANALYSIS")
        print("="*80)

        cursor.execute("""
            SELECT
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """)

        indexes = cursor.fetchall()
        current_table = None

        for schema, table, index_name, index_def in indexes:
            if table != current_table:
                print(f"\n📋 {table.upper()}:")
                current_table = table
            print(f"   {index_name}: {index_def}")

        # Check foreign key relationships
        print(f"\n\n🔗 FOREIGN KEY RELATIONSHIPS")
        print("="*80)

        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name;
        """)

        foreign_keys = cursor.fetchall()

        for table, column, ref_table, ref_column in foreign_keys:
            print(f"   {table}.{column} -> {ref_table}.{ref_column}")

        print("\n" + "="*80)
        print("✅ Schema analysis complete!")

        return tables

    except Exception as e:
        print(f"❌ Error analyzing schema: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def validate_backend_compatibility(tables: Dict):
    """Validate that the current schema matches backend models.py requirements"""

    print(f"\n\n🔍 BACKEND COMPATIBILITY VALIDATION")
    print("="*80)

    # Expected schema based on models.py
    expected_schema = {
        'users': [
            'id', 'email', 'password_hash', 'role', 'is_active', 'is_verified',
            'created_at', 'updated_at'
        ],
        'user_profiles': [
            'id', 'user_id', 'first_name', 'last_name', 'phone', 'address_line1',
            'address_line2', 'city', 'state', 'zip_code', 'emergency_contact_name',
            'emergency_contact_phone', 'fcm_token', 'square_customer_id',
            'created_at', 'updated_at'
        ],
        'documents': [
            'id', 'user_id', 'document_type', 'file_name', 'file_url', 'file_size',
            'verification_status', 'verified_by', 'verification_notes',
            'uploaded_at', 'verified_at'
        ],
        'verification_tokens': [
            'id', 'user_id', 'token', 'token_type', 'expires_at', 'used', 'created_at'
        ],
        'courses': [
            'id', 'title', 'description', 'duration_weeks', 'is_active',
            'created_at', 'updated_at'
        ],
        'enrollments': [
            'id', 'user_id', 'course_id', 'enrollment_date', 'status',
            'graduation_date', 'created_at', 'updated_at'
        ],
        'job_postings': [
            'id', 'title', 'company_name', 'description', 'requirements', 'location',
            'salary_min', 'salary_max', 'contact_email', 'is_active', 'posted_by',
            'posted_at', 'expires_at'
        ],
        'notifications': [
            'id', 'user_id', 'title', 'message', 'notification_type', 'is_read', 'created_at'
        ]
    }

    issues = []

    for table_name, expected_columns in expected_schema.items():
        if table_name not in tables:
            issues.append(f"❌ Missing table: {table_name}")
            continue

        print(f"\n📋 Validating {table_name.upper()}:")

        current_columns = [col['column_name'] for col in tables[table_name]]

        # Check for missing columns
        missing_columns = set(expected_columns) - set(current_columns)
        if missing_columns:
            for col in missing_columns:
                print(f"   ❌ Missing column: {col}")
                issues.append(f"Missing column {table_name}.{col}")

        # Check for extra columns (might be legacy)
        extra_columns = set(current_columns) - set(expected_columns)
        if extra_columns:
            for col in extra_columns:
                print(f"   ⚠️  Extra column: {col} (legacy?)")

        if not missing_columns and not extra_columns:
            print(f"   ✅ All required columns present")

    # Check for legacy tables
    legacy_tables = set(tables.keys()) - set(expected_schema.keys()) - {'alembic_version'}
    if legacy_tables:
        print(f"\n⚠️  LEGACY TABLES FOUND:")
        for table in legacy_tables:
            print(f"   - {table}")

    print(f"\n📊 VALIDATION SUMMARY:")
    if issues:
        print(f"   ❌ {len(issues)} issues found:")
        for issue in issues:
            print(f"     - {issue}")
    else:
        print(f"   ✅ Schema is compatible with backend models!")

    return len(issues) == 0

if __name__ == "__main__":
    print("🚀 Starting comprehensive database schema validation...")

    # Analyze current schema
    tables = analyze_database_schema()

    if tables:
        # Validate backend compatibility
        is_compatible = validate_backend_compatibility(tables)

        print(f"\n🎯 FINAL RESULT:")
        if is_compatible:
            print("✅ Database schema is ready for deployment!")
        else:
            print("⚠️  Database schema needs updates before deployment")

        sys.exit(0 if is_compatible else 1)
    else:
        print("❌ Failed to analyze database schema")
        sys.exit(1)