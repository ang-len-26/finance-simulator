import os

class FinTrackConfig:
    @staticmethod
    def get_admin_credentials():
        return {
            'username': os.getenv('ADMIN_USERNAME', 'admin'),
            'password': os.getenv('ADMIN_PASSWORD', 'changeme123'),
            'email': os.getenv('ADMIN_EMAIL', 'admin@fintrack.com')
        }
    
    @staticmethod
    def get_demo_credentials():
        return {
            'username': os.getenv('DEMO_USERNAME', 'demo'),
            'password': os.getenv('DEMO_PASSWORD', 'demo123')
        }