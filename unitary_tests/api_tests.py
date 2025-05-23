#!/usr/bin/env python3
import asyncio
import unittest
import json
import os
import sys
import requests
import time
from urllib.parse import urljoin
import io
from contextlib import redirect_stdout

# Configurações
BASE_URL = os.environ.get("TEST_API_URL", "http://localhost")
HEALTH_CHECK_TIMEOUT = 60  # segundos para aguardar que a API esteja pronta

class KVStoreAPITests(unittest.TestCase):
    """Testes unitários para a API de Key-Value Store"""
    
    @classmethod
    def setUpClass(cls):
        """Espera que a API esteja disponível antes de executar os testes"""
        print("🔍 Verificando se a API está disponível...")
        start_time = time.time()
        ready = False
        
        while time.time() - start_time < HEALTH_CHECK_TIMEOUT:
            try:
                response = requests.get(urljoin(BASE_URL, "/health/live"), timeout=2)
                if response.status_code == 200:
                    ready = True
                    break
            except requests.RequestException:
                pass
            
            time.sleep(1)
            sys.stdout.write(".")
            sys.stdout.flush()
        
        print("\n")
        if not ready:
            print("❌ API não está disponível após esperar. Impossível executar testes.")
            sys.exit(1)
        
        print("✅ API disponível! Iniciando testes...")
    
    def test_01_health_check(self):
        """Verifica se o health check está funcionando"""
        response = requests.get(urljoin(BASE_URL, "/health"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
    
    def test_02_liveness_check(self):
        """Verifica se o liveness check está funcionando"""
        response = requests.get(urljoin(BASE_URL, "/health/live"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "alive")
    
    def test_03_readiness_check(self):
        """Verifica se o readiness check está funcionando"""
        response = requests.get(urljoin(BASE_URL, "/health/ready"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ready")
    
    def test_04_cache_stats(self):
        """Verifica se as estatísticas de cache estão disponíveis"""
        response = requests.get(urljoin(BASE_URL, "/cache/stats"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("keys_count", data)
        self.assertIn("max_keys_limit", data)
        self.assertIn("memory_used_bytes", data)
    

    
 
    

    

def run_tests():
    """Executa os testes e retorna o resultado"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(KVStoreAPITests)
    
    # Silenciar a saída detalhada dos testes
    output_buffer = io.StringIO()
    
    # Redirecionar a saída padrão para o buffer durante a execução
    with redirect_stdout(output_buffer):
        runner = unittest.TextTestRunner(verbosity=0, stream=output_buffer)
        result = runner.run(suite)
    
    total_tests = result.testsRun
    passed_tests = total_tests - len(result.errors) - len(result.failures)
    
    # Exibir apenas uma mensagem sucinta com o resultado
    if result.wasSuccessful():
        print(f" {passed_tests} de {total_tests} testes passaram com sucesso!")
    else:
        print(f" {passed_tests} de {total_tests} testes passaram. Falhas detectadas.")
        # Mostrar as falhas, mas de forma resumida
        if result.failures:
            print("\nFalhas:")
            for i, (test, error) in enumerate(result.failures, 1):
                test_name = test._testMethodName
                print(f"  {i}. {test_name}: {error.splitlines()[-1] if error.splitlines() else 'Erro desconhecido'}")
        
        if result.errors:
            print("\nErros:")
            for i, (test, error) in enumerate(result.errors, 1):
                test_name = test._testMethodName
                print(f"  {i}. {test_name}: {error.splitlines()[-1] if error.splitlines() else 'Erro desconhecido'}")
    
    # Retornar código de saída apropriado
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 