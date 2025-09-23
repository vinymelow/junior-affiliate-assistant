# 🐍 GUIA DE INSTALAÇÃO DO PYTHON - Windows

## ❌ PROBLEMA IDENTIFICADO
O erro `pip : O termo 'pip' não é reconhecido` indica que o **Python não está instalado** ou não está configurado corretamente no seu sistema Windows.

## 🔧 SOLUÇÕES DISPONÍVEIS

### OPÇÃO 1: INSTALAÇÃO VIA MICROSOFT STORE (RECOMENDADA)
1. Abra o **Microsoft Store**
2. Pesquise por "**Python**"
3. Instale a versão mais recente (Python 3.11 ou 3.12)
4. Após a instalação, reinicie o terminal

### OPÇÃO 2: INSTALAÇÃO VIA SITE OFICIAL
1. Acesse: https://www.python.org/downloads/
2. Clique em "**Download Python 3.x.x**"
3. Execute o instalador baixado
4. **IMPORTANTE**: Marque a opção "**Add Python to PATH**"
5. Clique em "Install Now"
6. Reinicie o terminal após a instalação

### OPÇÃO 3: INSTALAÇÃO VIA CHOCOLATEY (PARA USUÁRIOS AVANÇADOS)
```powershell
# Instalar Chocolatey primeiro (se não tiver)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar Python
choco install python
```

## ✅ VERIFICAÇÃO DA INSTALAÇÃO

Após instalar o Python, execute estes comandos no terminal:

```powershell
# Verificar versão do Python
python --version

# Verificar se pip está funcionando
pip --version

# Listar pacotes instalados
pip list
```

## 🚀 PRÓXIMOS PASSOS APÓS INSTALAÇÃO

1. **Instalar dependências do projeto:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Testar o módulo de IA:**
   ```powershell
   python test_ai.py
   ```

3. **Iniciar o servidor:**
   ```powershell
   python -m uvicorn main:app --reload --port 8000
   ```

## 🔍 TROUBLESHOOTING

### Se ainda não funcionar após instalação:

1. **Reiniciar o terminal completamente**
2. **Verificar variáveis de ambiente:**
   ```powershell
   $env:PATH -split ';' | Where-Object { $_ -like '*Python*' }
   ```

3. **Usar caminho completo temporariamente:**
   ```powershell
   # Exemplo (ajuste o caminho conforme sua instalação)
   C:\Users\ronil\AppData\Local\Programs\Python\Python311\python.exe -m pip install -r requirements.txt
   ```

### Se o problema persistir:
- Desinstale e reinstale o Python
- Certifique-se de marcar "Add to PATH" durante a instalação
- Execute o PowerShell como Administrador

## 📋 COMANDOS ALTERNATIVOS

Se `pip` não funcionar, tente:
```powershell
# Usar módulo pip do Python
python -m pip install -r requirements.txt

# Ou usar py launcher (se disponível)
py -m pip install -r requirements.txt
```

## ⚠️ NOTA IMPORTANTE
O projeto **Junior Affiliate Assistant** requer Python 3.8 ou superior para funcionar corretamente. Certifique-se de instalar uma versão compatível.