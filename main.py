"""Entrypoint para o aplicativo Jumpscare.

Executa a janela principal do jumpscare importando o módulo modularizado
de `components`.
"""

from components.jumpscare import run_continuous


def main():
	# Roda continuamente; por padrão 1% a cada 1 segundo
	return run_continuous(probability=0.1, interval_seconds=1.0)


if __name__ == "__main__":
	raise SystemExit(main())
