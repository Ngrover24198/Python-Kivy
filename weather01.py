import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (ObjectProperty,ListProperty, StringProperty, NumericProperty)
from kivy.network.urlrequest import UrlRequest
from kivy.uix.listview import ListItemButton
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.uix.widget import Widget
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
import datetime
from kivy.uix.modalview import ModalView 

def locations_args_converter(index,data_item):  #this is a module level function
    city,country = data_item
    return {'location': (city,country)} # it returns a dictionary of key value pairs of data

class LocationButton(ListItemButton):
    location = ListProperty()

class AddLocationForm(ModalView): 
    search_input = ObjectProperty()
    search_results = ObjectProperty()

    def search_location(self):
        search_template = "http://api.openweathermap.org/data/2.5/"+"find?q={}&APPID=1f706b1080621f0c6262fa35f015b87d" # this is for searching the name or location only
        search_url = search_template.format(self.search_input.text)
        request = UrlRequest(search_url,self.found_location)

    def found_location(self,request,data):
        data = json.loads(data.decode()) if not isinstance(data,dict) else data
        cities = [(d['name'],d['sys']['country']) for d in data['list']]
        if not cities:
            self.search_results.item_strings = ["Nothing found"]
            print("Nothing Found..!!!!!!")
        else:
            self.search_results.item_strings = cities
        #print("\n".join(cities)) # this thing is just to print it in the terminal or get the output in the terminal
        self.search_results.adapter.data.clear()
        self.search_results.adapter.data.extend(cities)
        self.search_results._trigger_reset_populate()   
 
class CurrentWeather(BoxLayout):# now that we have declared this class here there is no need to use factory
    location = ListProperty(["Delhi","IN"])#you have to convert location to implicit list property i.e. converted the tuple in the list format
    conditions = StringProperty()
    temp = NumericProperty()
    temp_min = NumericProperty()
    temp_max = NumericProperty()
    conditions_image = StringProperty()

    def update_weather(self):
        config= Weather01App.get_running_app().config
        temp_type = config.getdefault("General","temp_type","metric").lower() # metric is the default unit
        weather_template = "http://api.openweathermap.org/data/2.5/"+"weather?q={},{}&units={}&APPID=1f706b1080621f0c6262fa35f015b87d"
        weather_url = weather_template.format(self.location[0],self.location[1],temp_type)
         # this *self will take only the arguements from the list of location
        request = UrlRequest(weather_url,self.weather_retrieved)

    def weather_retrieved(self,request,data):
        data = json.loads(data.decode()) if not isinstance(data,dict) else data
        self.conditions = data['weather'][0]['description']
        self.temp = data['main']['temp']
        self.temp_min = data['main']['temp_min']
        self.temp_max = data['main']['temp_max']
        self.conditions_image = "http://api.openweathermap.org/img/w/{}.png".format(data['weather'][0]['icon'])
 
class WeatherRoot(BoxLayout):
   
    current_weather = ObjectProperty()
    locations = ObjectProperty()
    forecast = ObjectProperty()
    carousel = ObjectProperty()
    add_location_form = ObjectProperty()

    def __init__(self,**kwargs):
        super(WeatherRoot,self).__init__(**kwargs)
        self.store = JsonStore("weather_store.json")
        if self.store.exists('locations'):
            locations = self.store.get('locations')
            self.locations.locations_list.adapter.data.extend(locations['locations'])
            current_location = locations["current_location"]
            self.show_current_weather(current_location)
        else:
            Clock.schedule_once(lambda dt: self.show_add_location_form())

    #def show_current_weather(self,location):   # recieved the self.text in the location variable, by default location is None
        #self.clear_widgets() # this is a kivy function in python to clear all the widgets from the screen
        #self.add_widget(Label(text = location)) # this line will print the location on the screen
        #if location is None and self.current_weather is None:
         #   location = ("Delhi","IN")
        #if location is not None:
            #self.current_weather = Factory.CurrentWeather() # linking with the dynamic class in kivy file using factory
         #   self.current_weather = CurrentWeather(location=location)   
        #if self.current_weather is None:  # this is the default cocndition
         #   self.current_weather = CurrentWeather()
        #if self.locations is None:
        #    self.locations = Factory.Locations()
         #   if (self.store.exists('locations')):
         #       locations = self.store.get("locations")['locations']
         #       self.locations.locations_list.adapter.data.extend(locations)

        #if location is not None:
         #   self.current_weather.location = location
         #   if location not in self.locations.locations_list.adapter.data:
         #       self.locations.locations_list.adapter.data.append(location)
        #        self.locations.locations_list._trigger_reset_populate()
        #        self.store.put("locations",locations=list(self.locations.locations_list.adapter.data),current_location=location)
        #self.current_weather.update_weather()
        #self.add_widget(self.current_weather)
    def show_current_weather(self,location):

        if location not in self.locations.locations_list.adapter.data:
            self.locations.locations_list.adapter.data.append(location)
            self.locations.locations_list._trigger_reset_populate()
            self.store.put("locations", locations=list(self.locations.locations_list.adapter.data),current_location=location)

        self.current_weather.location = location
        self.forecast.location = location 
        self.current_weather.update_weather()
        self.forecast.update_weather()

        self.carousel.load_slide(self.current_weather) 
        if self.add_location_form is not None: 
            self.add_location_form.dismiss()
 
    def show_add_location_form(self):
        self.add_location_form = AddLocationForm()
        self.add_location_form.open()

   # def show_locations(self):
   #     self.clear_widgets()
   #     self.add_widget(self.locations)
    
    #def show_forecast(self,location=None):
    #    self.clear_widgets()

    #        if location is None:
     #       self.forecast = Factory.Forecast()
        
     #   if location is not None:
     #       self.forecast.location = location
        
    #    self.forecast.update_weather()
     #   self.add_widget(self.forecast)

class Forecast(BoxLayout):
    location = ListProperty(["Delhi","IN"])
    forecast_container = ObjectProperty()

    def update_weather(self):
        config = Weather01App.get_running_app().config
        temp_type = config.getdefault("General","temp_type","Metric").lower()
        forecast_range = config.getdefault("General", "forecast_range", "3").lower()
        weather_template = "http://api.openweathermap.org/data/2.5/"+"forecast?q={},{}&units={}&cnt={}&APPID=1f706b1080621f0c6262fa35f015b87d"
        weather_url = weather_template.format(self.location[0], self.location[1], temp_type, forecast_range )
        request = UrlRequest(weather_url, self.weather_retrieved)

    def weather_retrieved(self, request, data):
        data = json.loads(data.decode()) if not isinstance(data, dict) else data
        self.forecast_container.clear_widgets()
        for day in data['list']:
            label = Factory.ForecastLabel()
            label.date = datetime.datetime.fromtimestamp(day['dt']).strftime("%a %b %d")
            label.conditions = day['weather'][0]['description']
            label.conditions_image = "http://openweathermap.org/img/w/{}.png".format(day['weather'][0]['icon'])
            label.temp_min = day['main']['temp_min']
            label.temp_max = day['main']['temp_max']
            self.forecast_container.add_widget(label)

class Weather01App(App):
    def build_config(self,config):
        config.setdefaults('General', {'temp_type': "Metric", "forecast_range": 3}) #by default temp_type is Metric and range is 3
    
    def build_settings(self,settings):
        settings.add_json_panel("Weather Settings", self.config, data="""
        [
            {"type" : "options" ,
            "title": "Temperature System",
            "section": "General",
            "key": "temp_type",
            "options": ["Metric","Imperial"]
            },
            {"type": "options",
             "title": "Forecast Range",
            "section": "General",
            "key": "forecast_range",
            "options": ["3", "5", "7"]
                }
        ]"""
        )
    
    def on_config_change(self,config,section,key,value):
        if config is self.config:
            if key == "temp_type":
                try:
                    self.root.current_weather.update_weather()
                    self.root.forecast.update_weather()
                except AttributeError:
                    pass
            if key == "forecast_range":
                try:
                    self.root.current_weather.update_weather()
                    self.root.forecast.update_weather()
                except AttributeError:
                    pass

if __name__=="__main__":
    Weather01App().run()
