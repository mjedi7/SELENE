from waitress import serve
from mysite.wsgi import application  # ya que tu proyecto se llama 'mysite'

serve(application, host='0.0.0.0', port=8000)