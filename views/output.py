from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import importlib
import linksLeft
import os, logging

def outputPageHTML(header, model, tables_html):
    """Generates HTML to fill '.articles_output' div on output page"""

    # Render output page view
    html = render_to_string('01uberheader.html', {
            'site_skin' : os.environ['SITE_SKIN'],
            'title': header+' Output'})
    html = html + render_to_string('02uberintroblock_wmodellinks.html', {
            'site_skin' : os.environ['SITE_SKIN'],
            'model':model,
            'page':'output'})
    html = html + linksLeft.linksLeft()
    html = html + render_to_string('04uberoutput_start.html', {
            'model_attributes': header+' Output'})
    html = html + tables_html
    html = html + render_to_string('export.html', {})
    html = html + render_to_string('04uberoutput_end.html', {'model':model})
    html = html + render_to_string('06uberfooter.html', {'links': ''})

    return html

def outputPageView(request, model='none', header=''):
    """
    Django view render method for model output pages
    """

    outputmodule = importlib.import_module('.'+model+'_output', 'models.'+model)
    tablesmodule = importlib.import_module('.'+model+'_tables', 'models.'+model)
    from REST import rest_funcs

    outputPageFunc = getattr(outputmodule, model+'OutputPage')      # function name = 'model'OutputPage  (e.g. 'sipOutputPage')
    model_obj = outputPageFunc(request)

    try:

        if type(model_obj) is tuple:
            modelOutputHTML = model_obj[0]
            model_obj = model_obj[1]

        else:
            if hasattr(model_obj, 'error'):
                logging.info('Error attribute is exists')

                modelOutputHTML = "<br>Error obtaining model results"
            else:
                modelOutputHTML = tablesmodule.timestamp(model_obj)
            
                tables_output = tablesmodule.table_all(model_obj)
            
                if type(tables_output) is tuple:
                    modelOutputHTML = modelOutputHTML + tables_output[0]
                elif type(tables_output) is str or type(tables_output) is unicode:
                    modelOutputHTML = modelOutputHTML + tables_output
                else:
                    modelOutputHTML = "<br>table_all() Returned Wrong Type"

    except Exception, e:
        logging.exception(e)

        modelOutputHTML = "<br>Error obtaining model results"

    # Render output page view
    html = outputPageHTML(header, model, modelOutputHTML)
    
    def saveToMongoDB(model_obj):
        """
        Method to check if model run is to be saved to MongoDB.  If true,
        the fest_func meothd to save the model object instance is called
        """
        # Handle Trex, which is not objectified yet; therefore, not saved in MongoDB
        if model != 'trex':
            # save_dic() rest_func method saves HTML & model object
            # rest_funcs.save_dic(html, model_obj.__dict__, model, "single")
            # save_model_object() rest_func method saves only the model object
            rest_funcs.save_model_object(model_obj.__dict__, model, "single")

    # Call method to save model object to Mongo DB
    saveToMongoDB(model_obj)

    response = HttpResponse()
    response.write(html)
    return response

@require_POST
def outputPage(request, model='none', header=''):
    """
    Django HTTP POST handler for output page.  Receives form data and
    validates it.  If valid it calls method to render the output page
    view.  If invalid, it returns the error to the model input page.
    """

    viewmodule = importlib.import_module('.views', 'models.'+model)

    header = viewmodule.header

    parametersmodule = importlib.import_module('.'+model+'_parameters', 'models.'+model)

    try:
        # Class name must be ModelInp, e.g. SipInp or TerrplantInp
        inputForm = getattr(parametersmodule, model.title() + 'Inp')
        form = inputForm(request.POST) # bind user inputs to form object

        # Form validation testing
        if form.is_valid():
            return outputPageView(request, model, header)

        else:
            logging.info(form.errors)
            inputmodule = importlib.import_module('.'+model+'_input', 'models.'+model)

            # Render input page view with POSTed values and show errors
            html = render_to_string('01uberheader.html', {
                    'site_skin' : os.environ['SITE_SKIN'],
                    'title': header+' Inputs'})
            html = html + render_to_string('02uberintroblock_wmodellinks.html', {
                    'site_skin' : os.environ['SITE_SKIN'],
                    'model':model,
                    'page':'input'})
            html = html + linksLeft.linksLeft()

            inputPageFunc = getattr(inputmodule, model+'InputPage')  # function name = 'model'InputPage  (e.g. 'sipInputPage')
            html = html + inputPageFunc(request, model, header, formData=request.POST)  # formData contains the already POSTed form data

            html = html + render_to_string('06uberfooter.html', {'links': ''})
            
            response = HttpResponse()
            response.write(html)
            return response

        # end form validation testing

    except Exception, e:
        logging.exception(e)
        logging.info("E X C E P T")

        return outputPageView(request, model, header)