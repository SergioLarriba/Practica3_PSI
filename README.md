# Practica3_PSI
Repositorio privado de la práctica 3 de Proyecto de Sistemas Informáticos

**Authors**:
- Sergio Larriba Moreno
- Javier Valero Velázquez

## Tests y Coverage

### Cómo ejecutar los tests:

1 - Activar el entorno virtual

2 - Exportar las variables TESTING y DATABASE_URL de la siguiente forma:
  - $ export TESTING=1
  - $ export DATABASE_URL=postgresql://sergio3c2003:KEyS7aWpN8hv@ep-autumn-resonance-a2nl6rut.eu-central-1.aws.neon.tech/p3_psi?sslmode=require

3 - Ejecutar en el entorno virtual coverage, en el mismo directorio donde se encuentra el archivo 'manage.py'
  - $ coverage erase
  - $ coverage run --omit="*/test*" --source=models ./manage.py test models.tests
  - $ coverage report -m -i




