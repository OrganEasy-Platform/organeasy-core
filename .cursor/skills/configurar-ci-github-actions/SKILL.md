---
name: configurar-ci-github-actions
description: Configura pipeline GitHub Actions para testes unitários Django/DRF, com UTF-8 em requirements e settings de CI. Use ao criar ou alterar CI, workflows .yml ou corrigir falha de encoding no Linux.
---

# Configurar CI GitHub Actions

Complementa `090-tests-auto.mdc` e `100-security-settings-always.mdc`.

CI roda **apenas** testes unitários (`-m "not integration"`). Integração fica fora do pipeline.

## Arquivos

| Arquivo | Função |
| ------- | ------ |
| `.github/workflows/ci.yml` | Pipeline |
| `requirements.txt` | UTF-8 obrigatório |
| `requirements-dev.txt` | UTF-8 obrigatório |
| `pytest.ini` / `pyproject.toml` | marker `integration` |
| `.env.example` | referência de variáveis para o CI |

## UTF-8 em requirements

UTF-16 quebra `pip install` no Linux (arquivos criados via PowerShell podem sair em UTF-16).

Verificar:

```powershell
python -c "b=open('requirements.txt','rb').read(2); print('UTF-16!' if b in (b'\xff\xfe', b'\xfe\xff') else 'OK')"
```

Corrigir:

```powershell
python -c "p='requirements.txt'; open(p,'w',encoding='utf-8',newline='\n').write(open(p,encoding='utf-16').read())"
```

## Step de verificação no workflow

```yaml
- name: Verify requirements files are UTF-8
  run: |
    python -c "
    import pathlib
    for name in ('requirements.txt', 'requirements-dev.txt'):
        p = pathlib.Path(name)
        if not p.exists():
            continue
        raw = p.read_bytes()
        if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
            raise SystemExit(f'{name} must be UTF-8, not UTF-16')
        raw.decode('utf-8')
    print('requirements encoding OK')
    "
```

## Pipeline — regras

- Secrets fictícios em `env:` do workflow (`SECRET_KEY=ci-secret`, `DEBUG=False`, banco de teste)
- `DJANGO_SETTINGS_MODULE` apontando para settings de CI/teste
- PostgreSQL como service container quando os testes exigirem banco
- `pytest -m "not integration" -v --tb=short` (pytest-django) ou `python manage.py test`
- Rodar `python manage.py makemigrations --check --dry-run` para detectar migration faltando
- Python alinhado ao projeto (ex. 3.12)
- Branches: main, master, develop

## `pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
testpaths = tests
markers =
    integration: testes contra banco/rede real (fora do CI)
```

## Ao criar/alterar CI

1. UTF-8 em requirements
2. Step de encoding
3. Settings/variáveis de CI sem secrets reais
4. Só unitários no CI
5. README (seção CI) + **Alterações recentes**
