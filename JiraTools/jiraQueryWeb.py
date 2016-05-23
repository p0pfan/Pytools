class JiraQueryWeb:
    _web_code={
    "tableCSS":
    '''
* {
  margin: 5px 0px;
  padding: 0;
  font-family: Lato;
}
body {
    padding: 0px;
  background: #FFFFFF;
  overflow-x: hidden;
  margin: 10px !important;
}
.table {

  border-collapse: collapse;
  margin: 0 0 10px 0;
  width: 100%;
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
  display: table;
  font-size: 100%;
  font-weight: bold;
  border-spacing: 0;
  
}

.flatTable {
  margin: 5px ;
  width: 100%;
  min-width: 800px;
  border-collapse: collapse;
  font-weight: bold;
  color: #6b6b6b;
}
.flatTable tr {
  height: 50px;
  background: #d4d1d5;
  border-bottom: rgba(0, 0, 0, 0.05) 1px solid;
}
.flatTable td {
  box-sizing: border-box;
  padding-left: 30px;
}
.flatTable .titleTr {
  height: 70px;
  color: #f6f3f7;
  background: #418a95;
  font-size: 14pt;
  border: 0px solid;
}

.flatTable .headingTr {
  height: 30px;
  background: #63acb7;
  color: #f6f3f7;
  font-size: 14pt;
  border: 0px solid;
}
    ''',
    
    "timelineCSS":
    '''

.wrap {
  margin: 0 auto;
  padding: 5%;
  background: #D4D1D5;
 
}
/* Bar Graph Class */
.barGraph {
  position: relative;
  width: 100%;
  height: auto;
  margin-bottom: 50px;
}
.graph {
  position: relative;
  list-style-type: none;
  padding: 0;
  margin: 0;
  width: calc(96%);
  left: 4%;
  z-index: 100;
}
.graph-barBack {
  border-radius: 2px;
  background: rgba(218, 228, 235, 0.64);
  margin-bottom: 10px;
  display: block;
  border-bottom: 1px solid #f6f3f7;
}
.graph-bar-fragment {
  -webkit-transition: all .4s ease-out;
  -moz-transition: all .4s ease-out;
  -o-transition: all .4s ease-out;
  transition: all .4s ease-out;
  width: 0;
  height: 30px;
  float: left;
  text-align: center;
  cursor: pointer;
  z-index: 10200;
  display: block;
  border-right: 1px solid #D7DDE3;
}


.graph-bar-fragment:hover {
  -webkit-transition: all 0.5s ease;
  -moz-transition: all 0.5s ease;
  -o-transition: all 0.5s ease;
  transition: all 0.5s ease;
  background: #428D92;
}

.graph-bar-fragment:after {

  background: #455a64;
  box-shadow: 0 1px 4px rgba(0,0,0,.37);
  color: rgba(255,255,255,.7);
  font: 14px/20px Roboto,sans-serif;
  position: absolute;
  transition: opacity .2s,visibility .2s;
  margin-top: 30px;
  
  content: attr(data-value);
  display: none;
  min-width: 50px;

}
.graph-bar-fragment:hover:after {
  display: block;
}

.graph-legend {
  position: absolute;
  left: -7%;
  width:7%;
  z-index: 9999;
}


.marker-number {
  position: relative;
  
  top: -10px;
  text-align: left;
  font-weight: bold;
}
.marker {
  -webkit-box-sizing: border-box;
  position: absolute;
  bottom: 0;
  top: -2em;
  width:6%;
  border-left: 2px solid #0E0E0E;
  z-index: 50;
}

.block {
    background: #c9575e;
    background: -moz-linear-gradient(top, #c9575e 0%, #c12e41 100%);
    background: -webkit-gradient(linear, left top, left bottom, color-stop(0%, #c9575e), color-stop(100%, #c12e41));
    background: -webkit-linear-gradient(top, #c9575e 0%, #c12e41 100%);
    background: -o-linear-gradient(top, #c9575e 0%, #c12e41 100%);
    background: -ms-linear-gradient(top, #c9575e 0%, #c12e41 100%);
    background: linear-gradient(to bottom, #c9575e 0%, #c12e41 100%);
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#c9575e', endColorstr='#c12e41',GradientType=0 );
}

.open {
    background: #d6ac6e;
    background: -moz-linear-gradient(top, #d6ac6e 0%, #cc9e52 100%);
    background: -webkit-gradient(linear, left top, left bottom, color-stop(0%, #d6ac6e), color-stop(100%, #cc9e52));
    background: -webkit-linear-gradient(top, #d6ac6e 0%, #cc9e52 100%);
    background: -o-linear-gradient(top, #d6ac6e 0%, #cc9e52 100%);
    background: -ms-linear-gradient(top, #d6ac6e 0%, #cc9e52 100%);
    background: linear-gradient(to bottom, #d6ac6e 0%, #cc9e52 100%);
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#d6ac6e', endColorstr='#cc9e52',GradientType=0 );
}
.inprogress {
    background: #6db683;
    background: -moz-linear-gradient(top, #6db683 0%, #569b6d 100%);
    background: -webkit-gradient(linear, left top, left bottom, color-stop(0%, #6db683), color-stop(100%, #569b6d));
    background: -webkit-linear-gradient(top, #6db683 0%, #569b6d 100%);
    background: -o-linear-gradient(top, #6db683 0%, #569b6d 100%);
    background: -ms-linear-gradient(top, #6db683 0%, #569b6d 100%);
    background: linear-gradient(to bottom, #6db683 0%, #569b6d 100%);
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#6db683', endColorstr='#569b6d',GradientType=0 );
}

.triaged {
    background: #7f8cc4;
    background: -moz-linear-gradient(top, #7f8cc4 0%, #6477ac 100%);
    background: -webkit-gradient(linear, left top, left bottom, color-stop(0%, #7f8cc4), color-stop(100%, #6477ac));
    background: -webkit-linear-gradient(top, #7f8cc4 0%, #6477ac 100%);
    background: -o-linear-gradient(top, #7f8cc4 0%, #6477ac 100%);
    background: -ms-linear-gradient(top, #7f8cc4 0%, #6477ac 100%);
    background: linear-gradient(to bottom, #7f8cc4 0%, #6477ac 100%);
    filter: progid:DXImageTransform.Microsoft.gradient( startColorstr='#7f8cc4', endColorstr='#6477ac',GradientType=0 );
}
.empty{
  background: rgb(215, 221, 227);;
}


#wrap{
  font-weight: bold;
  word-break:break-all;
  width:100%; 
  overflow:auto;
}
.read-more-state {
  display: none;
}

.read-more-target {
  opacity: 0;
  max-height: 0;
  font-size: 0;
  transition: .25s ease;
}

.read-more-state:checked ~ .read-more-wrap .read-more-target {
  opacity: 1;
  font-size: inherit;
  max-height: 999em;
}

.read-more-state ~ .read-more-trigger:before {
  content: 'Show more';
}

.read-more-state:checked ~ .read-more-trigger:before {
  content: 'Show less';
}

.read-more-trigger {
  cursor: pointer;
  display: inline-block;
  padding: 0 .5em;
  color: #666;
  font-size: .9em;
  line-height: 2;
  border: 1px solid #000000;
  border-radius: .25em;
}
    ''' ,
            
    "HTML_head":
    '''
<html >
  <head>
    <meta charset="UTF-8">
    <title>Jira Task&Timeline</title>
        <link rel="stylesheet" href="style.css">
        <link rel="stylesheet" href="timeline.css">
    <style>
      A:link{text-decoration:none;color: #000000;}
      A:visited{text-decoration:none;color: #000000;}
      A:hover {text-decoration:underline;color: #FFFFFF;}
    </style>

  </head>
  <body>
    ''' ,
              
    "HTML_end":
    '''
<link href='http://fonts.googleapis.com/css?family=Lato:100,300,400,700,900' rel='stylesheet' type='text/css'>
    <script src='http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js'></script>

  </body>
</html>       
    ''',

    "whole_timeline_head":
    '''
  <br>
  <br>
  <br>
  <div class="wrap">  
    <div class="barGraph">
      <ul class="graph">    
    ''' ,
    
    "whole_timeline_end":
    '''
      </ul> 
        <div class="marker" style="left: 10%;">
          <span class="marker-number">9:00-9:30</span>
        </div>      
        <div class="marker" style="left: 16%;">
          <span class="marker-number">9:30-10:00</span>
        </div>
        <div class="marker" style="left: 22%;">
          <span class="marker-number">10:00-10:30</span>
        </div>  
        <div class="marker" style="left: 28%;">
          <span class="marker-number">10:30-11:00</span>
        </div>  
        <div class="marker" style="left: 34%;">
          <span class="marker-number">11:00-11:30</span>
        </div>  
        <div class="marker" style="left: 40%;">
          <span class="marker-number">13:30-14:00</span>
        </div>  
        <div class="marker" style="left: 46%;">
          <span class="marker-number">14:00-14:30</span>
        </div>  
        <div class="marker" style="left: 52%;">
          <span class="marker-number">14:30-15:00</span>
        </div>  
        <div class="marker" style="left: 58%;">
          <span class="marker-number">15:00-15:30</span>
        </div>  
        <div class="marker" style="left: 64%;">
          <span class="marker-number">15:30-16:00</span>
        </div>  
        <div class="marker" style="left: 70%;">
          <span class="marker-number">16:00-16:30</span>
        </div>  
        <div class="marker" style="left: 76%;">
          <span class="marker-number">16:30-17:00</span>
        </div>  
        <div class="marker" style="left: 82%;">
          <span class="marker-number">17:00-17:30</span>
        </div>  
        <div class="marker" style="left: 88%;">
          <span class="marker-number">17:30-18:00</span>
        </div> 
        <div class="marker" style="left: 94%;">
          <span class="marker-number"></span>
        </div>  
    </div>  
  </div>   
    ''',
       
    "one_timeline_head":
    '''
        <!-- the timeline of one person -->
        <span class="graph-barBack">     
    ''',
    
    "one_timeline_end":
    '''
        </span>    
    ''',
}
    
    def __init__(self):
        pass
    
    def __getitem__(self,codename):
        keys_table = self._web_code.keys()
        
        found_key=None        
        for key in keys_table:
            if(codename == key):
                found_key=key
                break
            
        if(None == found_key):
            return None
        
        return self._web_code[found_key]
               
    
    
    