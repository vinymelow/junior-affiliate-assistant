"""
Detector de gênero baseado em nomes brasileiros
"""

def detect_gender_from_name(name: str) -> str:
    """
    Detecta o gênero baseado no primeiro nome
    Retorna 'M' para masculino, 'F' para feminino, 'N' para neutro/desconhecido
    """
    if not name or not isinstance(name, str):
        return 'N'
    
    # Pega apenas o primeiro nome e normaliza
    first_name = name.strip().split()[0].lower()
    
    # Nomes tipicamente masculinos
    male_names = {
        'joão', 'josé', 'antonio', 'francisco', 'carlos', 'paulo', 'pedro', 'lucas', 'luiz',
        'marcos', 'luis', 'gabriel', 'rafael', 'daniel', 'marcelo', 'bruno', 'eduardo',
        'felipe', 'raimundo', 'rodrigo', 'manoel', 'nelson', 'roberto', 'fabio', 'alessandro',
        'andre', 'fernando', 'gustavo', 'diego', 'leonardo', 'sergio', 'fabiano', 'paulo',
        'ricardo', 'jorge', 'alexandre', 'adriano', 'thiago', 'leandro', 'ivan', 'wesley',
        'vinicius', 'mateus', 'guilherme', 'anderson', 'julio', 'cesar', 'renato', 'diego',
        'caio', 'henrique', 'arthur', 'enzo', 'miguel', 'davi', 'bernardo', 'samuel',
        'theo', 'nicolas', 'lorenzo', 'pietro', 'benjamin', 'matheus', 'heitor', 'ryan',
        'ravi', 'gael', 'anthony', 'joão', 'pedro', 'lucas', 'gabriel', 'miguel', 'arthur',
        'heitor', 'lorenzo', 'theo', 'davi', 'bernardo', 'noah', 'samuel', 'enzo', 'vicente',
        'antonio', 'angel', 'jose', 'joaquim', 'benicio', 'nicolas', 'felipe', 'levi',
        'pietro', 'benjamin', 'matheus', 'isaac', 'daniel', 'henry', 'ryan', 'ravi'
    }
    
    # Nomes tipicamente femininos
    female_names = {
        'maria', 'ana', 'francisca', 'antonia', 'adriana', 'juliana', 'marcia', 'fernanda',
        'patricia', 'aline', 'sandra', 'camila', 'amanda', 'bruna', 'jessica', 'leticia',
        'julia', 'luciana', 'vanessa', 'mariana', 'gabriela', 'valeria', 'adriane', 'carla',
        'barbara', 'viviane', 'rosangela', 'sueli', 'luana', 'simone', 'monica', 'andrea',
        'cristiane', 'michele', 'tatiane', 'renata', 'daniela', 'claudia', 'eliane', 'raquel',
        'sabrina', 'priscila', 'karina', 'bianca', 'larissa', 'natalia', 'carolina', 'isabela',
        'beatriz', 'vitoria', 'giovanna', 'alice', 'manuela', 'sophia', 'helena', 'valentina',
        'laura', 'isabella', 'luiza', 'heloisa', 'livia', 'cecilia', 'eloisa', 'lara',
        'antonella', 'rafaela', 'maria', 'clara', 'ana', 'julia', 'sophia', 'isabella',
        'manuela', 'giovanna', 'alice', 'laura', 'luiza', 'helena', 'valentina', 'heloisa',
        'beatriz', 'maria', 'cecilia', 'eloisa', 'lara', 'antonella', 'rafaela', 'esther',
        'emanuelly', 'anna', 'rebeca', 'sarah', 'elisa', 'antonela', 'isis', 'alicia',
        'melissa', 'agatha', 'maitê', 'nicole', 'luna', 'pietra', 'marina', 'nina'
    }
    
    # Verifica se o nome está nas listas
    if first_name in male_names:
        return 'M'
    elif first_name in female_names:
        return 'F'
    
    # Regras baseadas em terminações comuns
    # Terminações tipicamente femininas
    if first_name.endswith(('a', 'ana', 'ina', 'iana', 'ella', 'lla', 'cia', 'tia', 'ria')):
        # Exceções masculinas que terminam em 'a'
        male_exceptions = {'luca', 'joshua', 'noah', 'elias', 'jonas', 'thomas', 'nicolas', 'matias'}
        if first_name not in male_exceptions:
            return 'F'
    
    # Terminações tipicamente masculinas
    if first_name.endswith(('o', 'os', 'or', 'er', 'an', 'on', 'el', 'il', 'ul')):
        return 'M'
    
    # Se não conseguiu determinar, retorna neutro
    return 'N'


def get_appropriate_greeting(name: str, gender: str = None) -> dict:
    """
    Retorna saudações apropriadas baseadas no gênero
    """
    if not gender or gender == 'N':
        gender = detect_gender_from_name(name)
    
    if gender == 'M':
        return {
            'casual': ['mano', 'parça', 'cara', 'brother'],
            'formal': ['parceiro', 'amigo'],
            'slang': ['parça', 'mano', 'bro']
        }
    elif gender == 'F':
        return {
            'casual': ['mana', 'amiga', 'garota', 'sister'],
            'formal': ['parceira', 'amiga'],
            'slang': ['mana', 'amiga', 'sis']
        }
    else:
        # Neutro - evita formas genéricas como "parceiro(a)"
        return {
            'casual': ['pessoal', 'galera'],
            'formal': ['pessoa', 'amigo'],
            'slang': ['galera', 'pessoal']
        }