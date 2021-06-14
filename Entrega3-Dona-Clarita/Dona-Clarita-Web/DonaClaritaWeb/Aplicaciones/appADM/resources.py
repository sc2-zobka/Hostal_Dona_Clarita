from import_export import resources  
from Aplicaciones.app.models import Huesped  

class HuespedResource(resources.ModelResource):  
   class Meta:  
      model = Huesped 