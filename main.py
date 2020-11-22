from aiohttp import web
import aiohttp_jinja2
import jinja2
import json
from mcstatus import MinecraftServer
routes = web.RouteTableDef()


app = web.Application()

jinja_env = aiohttp_jinja2.setup(app,
  loader=jinja2.FileSystemLoader('templates'))

print(type(jinja_env))
print(jinja_env)

color_codes = {
  '0': '#000000',
  '1': '#0000be',
  '2': '#00be00',
  '3': '#00bebe',
  '4': '#be0000',
  '5': '#be00be',
  '6': '#ffaa00',
  '7': '#bebebe',
  '8': '#3f3f3f',
  '9': '#3f3ffe',
  'a': '#3ffe3f',
  'b': '#3ffefe',
  'c': '#fe3f3f',
  'd': '#fe3ffe',
  'e': '#fefe3f',
  'f': '#ffffff'  
}



other_style_codes = {
    'l': 'font-weight: bold;'
}

def json_color_codes(json_object):
  print('yess')
  if isinstance(json_object, list):
    things = []
    for thing in json_object:
      things.append(json_color_codes(thing))
    return ''.join(things)

  style = []
  if json_object.get('bold'):
    style.append('font-weight: bold')
  if json_object.get('color'): style.append('color: ' + json_object['color'])
  inHtml = json_object['text']
  if 'extra' in json_object:
    inHtml += json_color_codes(json_object['extra'])
  html = ''
  if style:
    joinedStyles = ';'.join(style)
    html += f'<span style="{joinedStyles}">'
  html += inHtml
  if style:
    html += '</span>'
  return html

def convert_color_codes_to_html(code, symbol, include_raw=False):
    current_color = None
    current_effects = set()
    if not isinstance(code, str):
        print(code)
        code = code.decode()
    print(code)
    output = ''
    text_output = ''
    i = -1
    while i < len(code) - 1:
        i += 1
        if code[i] == symbol:
            i += 1
            if code[i] in color_codes:
                if current_color:
                    output += '</span>'
                color = color_codes[code[i]]
                style = f'color:{color}'
            elif code[i] in other_style_codes:
                current_effects.add(code[i])
                style = other_style_codes[code[i]]
            output += f'<span style="{style}">'
            current_color = color
        else:
            output += code[i]
            text_output += code[i]
    if current_color:
        output += '</span>'
    if include_raw:
        return output, text_output
    return output

def cctohtm(code, symbol, include_raw=False):
  if isinstance(code, dict):
    return json_color_codes(code)
  if isinstance(code, str):
    return convert_color_codes_to_html(code, symbol)
  


jinja_env.globals[
  'convert_color_codes_to_html'] = cctohtm


@routes.get('/')
@aiohttp_jinja2.template('index.html')
def index(request):
  return {}

@routes.get('/server')
@aiohttp_jinja2.template('stats.html')
async def server(request):
  ip = request.rel_url.query['ip']
  serverObject = MinecraftServer.lookup(ip)
  s = await serverObject.async_status()
  return {'s': s, 'ip': ip}

app.add_routes(routes)
web.run_app(app)