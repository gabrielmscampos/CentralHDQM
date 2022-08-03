import sys
from collections import defaultdict
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
app = Flask(__name__)

CORS(app)

import db

###
@app.route('/api/data', methods=['GET'])
def get_data( json = True ):
  if not json :
    pd = "MinimumBias"
    processing_string = "PromptReco"
    latest = 50
    subsystem = "SiStrips"
    from_run = 1
    to_run = 999999
    runs = None
    #runs = [ 355708, 355710, 355711 ]
    latest = 50
    series = 355711
    series_id = None
  else : 
    ### old HDQM code
    subsystem = request.args.get('subsystem')
    pd = request.args.get('pd')
    processing_string = request.args.get('processing_string')
    from_run = request.args.get('from_run', type=int)
    to_run = request.args.get('to_run', type=int)
    runs = request.args.get('runs')
    latest = request.args.get('latest', type=int)
    series = request.args.get('series')
    series_id = request.args.get('series_id', type=int)
    series_id = None

    if series_id == None:
      if subsystem == None:
        return jsonify({'message': 'Please provide a subsystem parameter.'}), 400

      if pd == None:
        return jsonify({'message': 'Please provide a pd parameter.'}), 400

      if processing_string == None:
        return jsonify({'message': 'Please provide a processing_string parameter.'}), 400

    modes = 0
    if from_run != None and to_run != None: modes += 1
    if latest != None: modes += 1
    if runs != None: modes += 1

    if modes > 1:
      return jsonify({'message': 'The combination of parameters you provided is invalid.'}), 400

    if runs != None:
      try:
        runs = runs.split(',')
        runs = [int(x) for x in runs]
      except:
        return jsonify({'message': 'runs parameter is not valid. It has to be a comma separated list of integers.'}), 400

    if series and series_id:
      return jsonify({'message': 'series and series_id can not be defined at the same time.'}), 400

  ### runs
  if latest == None:
    latest = 50

  if runs:
    runs = db.session.query( db.Run ).filter( db.Run.id.in_( runs ) ).all()
  elif from_run and to_run :
    runs = db.session.query( db.Run ).where( db.Run.id >= from_run, db.Run.id <= to_run ).all()
  else :
    runs = db.session.query( db.Run ).order_by( db.Run.id.desc() ).limit( latest ).all()
  
  print( [ run.id for run in runs ] )
  ### datasets
  dataset = db.session.query( db.Dataset ).where( db.Dataset.stream == pd, db.Dataset.reco_path == processing_string).first()

  ### trends & configs
  trends_and_configs = db.session.query( db.Trend, db.Config ).where( db.Trend.dataset_id == dataset.id, db.Trend.subsystem == subsystem).filter( db.Trend.config_id == db.Config.id ).all()
  
  ### calc results
  result = []
  for trend, config in trends_and_configs:
    points = eval(trend.points)
    trends_data = []

    for run in reversed(runs):

      if not run.rr_significant : continue

      point = points.get(run.id, None)
      if not point : continue

      dat = {
        'run': int(run.id),
        'value': float(point[0]),
        'error': float(point[1]),
        'oms_info': eval(run.oms_data),
      }
      trends_data.append( dat )

    # if not trends_data : continue

    result += [ {
      'metadata': { 
        'y_title': config.y_title, 
        'plot_title': config.plot_title, 
        'name': config.name, 
        'subsystem': subsystem, 
        'pd': pd, ### why we return what we requested ???
        'processing_string': processing_string,
        },
      'trends': trends_data } ]

  if json : return jsonify(result)
  return result 
      
### 
@app.route('/api/selection', methods=['GET'])
def get_selections( json = True ):
  #try:
    subsystems = db.session.query( db.Config.subsystem ).distinct().all()
    datasets = db.session.query( db.Dataset.id, db.Dataset.stream, db.Dataset.reco_path ).distinct().all()

    trends = db.session.query( db.Trend.dataset_id, db.Trend.subsystem ).where( db.Trend.points != "{}").all()
    trends_dic = {}
    for trend in trends:
      trends_dic[ str(trend.dataset_id) + "_" + str(trend.subsystem) ] = 1

    obj = defaultdict(lambda: defaultdict(list))
    for s in subsystems:
      for d in datasets:
        key = str(d.id) + "_" + str(s.subsystem)
        if key not in trends_dic: continue
        obj[ s.subsystem ][ d.stream ].append( d.reco_path )

    if json : return jsonify(obj)
    return obj 
  #except:
  #  pass

###
@app.route('/api/plot_selection', methods=['GET'])
def plot_selection():
  return jsonify({'message': 'Not supported'}), 500

### 
@app.route('/api/runs', methods=['GET'])
def get_runs( json = True  ):
  runs = [ r.id for r in db.session.query( db.Run.id ).order_by( db.Run.id.asc() ) ]
  if json : return jsonify(runs)
  return runs 

###
@app.route('/api/expand_url', methods=['GET'])
def expand_url():
  return jsonify({'message': 'Not supported'}), 500

  valid_url_types = [
    'main_gui_url', 'main_image_url', 
    'optional1_gui_url', 'optional1_image_url', 
    'optional2_gui_url', 'optional2_image_url', 
    'reference_gui_url', 'reference_image_url'
  ]

  url_type = request.args.get('url_type')
  run = request.args.get('run', type=int)
  dataset = request.args.get('dataset', type=str)
  me_path = request.args.get('me_path', type=str)

  if url_type not in valid_url_types:
    return jsonify({
      'message': 'Please provide a valid url_type parameter. Accepted values are: %s' % ','.join(valid_url_types)
    }), 400

  if run == None:
    return jsonify({'message': 'Please provide a run parameter.'}), 400

  if dataset == None:
    return jsonify({'message': 'Please provide a dataset parameter.'}), 400

  if me_path == None:
    return jsonify({'message': 'Please provide a me_path parameter.'}), 400

  plot_folder = '/'.join(me_path.split('/')[:-1])
  DQMGUI = 'https://cmsweb.cern.ch/dqm/offline/'
  gui_url = '%sstart?runnr=%s;dataset=%s;workspace=Everything;root=%s;focus=%s;zoom=yes;' % (DQMGUI, run, dataset, plot_folder, me_path)
  image_url = '%splotfairy/archive/%s%s/%s?v=1510330581101995531;w=1906;h=933' % (DQMGUI, run, dataset, me_path)

  return jsonify({'message': 'Error getting the url from the DB.'}), 500

### 
@app.route('/api/')
def index():
  return jsonify('HDQM REST API')

def do_tests():
  print("HDQM API do some tests ... ")
  print( "Subsystems ... " )
  subsystems = get_selections( False )
  print( subsystems )
  print( "Runs ... " )
  runs = get_runs( False )
  print( runs )
  print( "Data ... " )
  data = get_data( False)
  print( data )
  pass

if __name__ == '__main__':
  #do_tests()
  #exit()

  port=5000
  if len(sys.argv) >= 2:
    port=int(sys.argv[1])
  app.run(host='127.0.0.1', port=port)
