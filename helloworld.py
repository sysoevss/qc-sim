from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import quantumcomputation

import os



class MainPage(webapp.RequestHandler):
      
    def get(self):
        template_values = {
        }

        path = os.path.join(os.path.dirname(__file__), 'content.html')
        self.response.out.write(template.render(path, template_values))

class Compute(webapp.RequestHandler):
      
    def get(self):
        QC = quantumcomputation.QC(self.request.get('guid'))
        schema = self.request.get('schema')
        schema = ''.join(schema.split())
        schema = schema.replace(',}', '}')
        schema = schema.replace('------', 'I')
        
        n = len(schema.split('}')[0][1:].replace(',', ''))

        gates = schema.split('}')[1][1:].split(',')
        size = len(gates)
        tacts = size / n
        
        res = '{' + schema.split('}')[0][1:] + '}{'
        for i in range(tacts):
            for j in range(n):
                res += gates[tacts * j + i] + ','
                
        res = res[0:-1] + '}'
        
        state, n, N = QC.createState(res)
        state = QC.applyScheme(state, res, n) 
        classic_result = QC.measure(state)
        
        self.response.out.write(classic_result[-n:])

application = webapp.WSGIApplication([('/', MainPage), ('/compute/', Compute)], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
