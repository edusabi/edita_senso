import requests

BASE_URL = "https://pjfaculpytho.discloud.app/api"


def get_population_by_uf():
    """Obter população por UF."""
    try:
        response = requests.get(f"{BASE_URL}/population_by_uf")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao obter população por UF: {e}")
        return []

def get_by_uf(uf):
    """Obter dados de um estado (UF)."""
    try:
        response = requests.get(f"{BASE_URL}/estado/{uf}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao obter dados do estado {uf}: {e}")
        return {'error': str(e)}

def update_uf(uf, data):
    """Atualizar dados de um estado (UF)."""
    try:
        response = requests.put(f"{BASE_URL}/estado/{uf}", json=data)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Erro ao atualizar estado {uf}: {e}")
        return False

def delete_uf(uf):
    """Deletar dados de um estado (UF)."""
    try:
        response = requests.delete(f"{BASE_URL}/estado/{uf}")
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Erro ao deletar estado {uf}: {e}")
        return False

def get_rankings():
    """Obter os dados de rankings e insights."""
    try:
        response = requests.get(f"{BASE_URL}/rankings")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao obter rankings: {e}")
        return None