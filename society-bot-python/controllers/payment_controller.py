"""
============================================
Payment Controller - Database Operations
============================================

This module handles all database operations for
the Society Payment Tracker Bot.

Features:
- Insert new payments
- Retrieve payment records
- Daily and monthly summaries
- Member-specific queries
- Data export functionality
- Reset/clear operations
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from config.db import get_cursor

# Configure logging
logger = logging.getLogger(__name__)


class PaymentController:
    """Controller for payment database operations."""
    
    @staticmethod
    def insert_payment(member_name: str, amount: float, recorded_by: int) -> Dict[str, Any]:
        """
        Insert a new payment record into the database.
        
        Args:
            member_name: Name of the member
            amount: Payment amount
            recorded_by: Telegram user ID who recorded the payment
            
        Returns:
            Dict with inserted payment details
        """
        insert_query = """
            INSERT INTO society_payments (member_name, amount, recorded_by)
            VALUES (%s, %s, %s)
        """
        
        select_query = "SELECT * FROM society_payments WHERE id = %s"
        
        try:
            with get_cursor() as cursor:
                cursor.execute(insert_query, (member_name, amount, recorded_by))
                inserted_id = cursor.lastrowid
                
                # Retrieve the inserted record
                cursor.execute(select_query, (inserted_id,))
                payment = cursor.fetchone()
                
            logger.info(f"✅ Payment inserted: {member_name} - Rs.{amount} (ID: {inserted_id})")
            return payment
            
        except Exception as e:
            logger.error(f"❌ Error inserting payment: {e}")
            raise
    
    @staticmethod
    def get_last_payments(limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get the last N payment records.
        
        Args:
            limit: Number of records to retrieve
            
        Returns:
            List of payment records
        """
        query = """
            SELECT id, member_name, amount, recorded_by, payment_date
            FROM society_payments
            ORDER BY payment_date DESC
            LIMIT %s
        """
        
        try:
            with get_cursor() as cursor:
                cursor.execute(query, (limit,))
                payments = cursor.fetchall()
                
            logger.info(f"📊 Retrieved {len(payments)} payment records")
            return payments
            
        except Exception as e:
            logger.error(f"❌ Error fetching payments: {e}")
            raise
    
    @staticmethod
    def get_today_total() -> Dict[str, Any]:
        """
        Get today's total collection.
        
        Returns:
            Dict with total amount and count
        """
        query = """
            SELECT 
                COALESCE(SUM(amount), 0) as total,
                COUNT(*) as count
            FROM society_payments
            WHERE DATE(payment_date) = CURDATE()
        """
        
        try:
            with get_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                
            result = {
                'total': float(row['total']) if row['total'] else 0.0,
                'count': int(row['count']) if row['count'] else 0,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            logger.info(f"📅 Today's total: Rs.{result['total']} ({result['count']} payments)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error fetching today's total: {e}")
            raise
    
    @staticmethod
    def get_month_total() -> Dict[str, Any]:
        """
        Get current month's total collection.
        
        Returns:
            Dict with total amount, count, and month info
        """
        query = """
            SELECT 
                COALESCE(SUM(amount), 0) as total,
                COUNT(*) as count,
                MONTHNAME(CURRENT_DATE()) as month_name,
                YEAR(CURRENT_DATE()) as year
            FROM society_payments
            WHERE MONTH(payment_date) = MONTH(CURRENT_DATE())
            AND YEAR(payment_date) = YEAR(CURRENT_DATE())
        """
        
        try:
            with get_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                
            result = {
                'total': float(row['total']) if row['total'] else 0.0,
                'count': int(row['count']) if row['count'] else 0,
                'month_name': row['month_name'],
                'year': row['year']
            }
            
            logger.info(f"📆 {result['month_name']} {result['year']} total: Rs.{result['total']} ({result['count']} payments)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error fetching month total: {e}")
            raise
    
    @staticmethod
    def get_member_payments(member_name: str) -> Dict[str, Any]:
        """
        Get all payments for a specific member.
        
        Args:
            member_name: Name of the member (case-insensitive)
            
        Returns:
            Dict with payments array and summary
        """
        payments_query = """
            SELECT id, member_name, amount, recorded_by, payment_date
            FROM society_payments
            WHERE LOWER(member_name) = LOWER(%s)
            ORDER BY payment_date DESC
        """
        
        summary_query = """
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(amount), 0) as total
            FROM society_payments
            WHERE LOWER(member_name) = LOWER(%s)
        """
        
        try:
            with get_cursor() as cursor:
                cursor.execute(payments_query, (member_name,))
                payments = cursor.fetchall()
                
                cursor.execute(summary_query, (member_name,))
                summary = cursor.fetchone()
                
            result = {
                'member_name': member_name,
                'payments': payments,
                'total_payments': int(summary['count']) if summary['count'] else 0,
                'total_amount': float(summary['total']) if summary['total'] else 0.0
            }
            
            logger.info(f"👤 {member_name}: {result['total_payments']} payments, total Rs.{result['total_amount']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error fetching member payments: {e}")
            raise
    
    @staticmethod
    def get_all_payments() -> List[Dict[str, Any]]:
        """
        Get all payment records for export.
        
        Returns:
            List of all payment records
        """
        query = """
            SELECT id, member_name, amount, recorded_by, payment_date
            FROM society_payments
            ORDER BY payment_date DESC
        """
        
        try:
            with get_cursor() as cursor:
                cursor.execute(query)
                payments = cursor.fetchall()
                
            logger.info(f"📤 Exporting {len(payments)} payment records")
            return payments
            
        except Exception as e:
            logger.error(f"❌ Error fetching all payments: {e}")
            raise
    
    @staticmethod
    def reset_all_payments() -> Dict[str, int]:
        """
        Delete all payment records (reset).
        
        Returns:
            Dict with number of deleted records
        """
        count_query = "SELECT COUNT(*) as count FROM society_payments"
        truncate_query = "TRUNCATE TABLE society_payments"
        
        try:
            with get_cursor() as cursor:
                # Get count first
                cursor.execute(count_query)
                count_result = cursor.fetchone()
                deleted_count = int(count_result['count']) if count_result['count'] else 0
                
                # Truncate table
                cursor.execute(truncate_query)
                
            logger.info(f"🗑️ Deleted {deleted_count} payment records")
            return {'deleted_count': deleted_count}
            
        except Exception as e:
            logger.error(f"❌ Error resetting payments: {e}")
            raise
    
    @staticmethod
    def get_payment_stats() -> Dict[str, Any]:
        """
        Get payment statistics summary.
        
        Returns:
            Dict with various statistics
        """
        query = """
            SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(amount), 0) as total_amount,
                COALESCE(AVG(amount), 0) as avg_amount,
                COALESCE(MAX(amount), 0) as max_amount,
                COALESCE(MIN(amount), 0) as min_amount,
                COUNT(DISTINCT member_name) as unique_members
            FROM society_payments
        """
        
        try:
            with get_cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
                
            return {
                'total_payments': int(row['total_count']) if row['total_count'] else 0,
                'total_amount': float(row['total_amount']) if row['total_amount'] else 0.0,
                'average_amount': float(row['avg_amount']) if row['avg_amount'] else 0.0,
                'max_amount': float(row['max_amount']) if row['max_amount'] else 0.0,
                'min_amount': float(row['min_amount']) if row['min_amount'] else 0.0,
                'unique_members': int(row['unique_members']) if row['unique_members'] else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching payment stats: {e}")
            raise


# Create a singleton instance for convenience
payment_controller = PaymentController()
