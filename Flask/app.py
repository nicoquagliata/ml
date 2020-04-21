# import the necessary packages
import tensorflow as tf
from keras.models import load_model
from PIL import Image
import numpy as np
import flask
import io
import os

# initialize our Flask application and the Keras model
app = flask.Flask(__name__)
model = None

# set the port dynamically with a default of 5000 for local development
port = int(os.getenv('PORT', '8080'))

def load_model_from_file():
    # load the  Keras model
    global model
    #model = load_model('models/famosos_cnn.h5')
    model = load_model('models/model.h5')
    # save the graph after loading the model
    global graph
    graph = tf.get_default_graph()

def prepare_image(image, target):
    # if the image mode is not RGB, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")

    # resize the input image and preprocess it
    image = image.resize(target)
    image = np.asarray(image)

    # return the processed image
    return image

@app.route("/predict", methods=["POST"])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("imagen"):
            class_names = ['Leonardo', 'Nicolas', 'Ricardo']
            images_predict = []
            # read the image in PIL format
            image = flask.request.files["imagen"].read()
            image = Image.open(io.BytesIO(image))

            # preprocess the image and prepare it for classification
            image = prepare_image(image, target=(224, 224))
            images_predict.append(image)
            images_predict = np.asarray(images_predict)
            
            # classify the input image and then initialize the list
            # of predictions to return to the client
            with graph.as_default():
                preds = model.predict(images_predict)
                print(preds)
                #data["predictions"] = []
                data["images"] = [{ "classifiers": [ { "classes" : [] } ]}]


                # loop over the results and add them to the list of
                # returned predictions
                for i in range(len(preds[0])):
                    #r = {"type": class_names[i], "probability": float(preds[0][i])}
                    #data["predictions"].append(r)
                    r = {"class": class_names[i], "score": float(preds[0][i])}
                    data["images"][0]["classifiers"][0]["classes"].append(r)


                # indicate that the request was a success
                data["success"] = True

    # return the data dictionary as a JSON response
    response = flask.jsonify(data)
    print(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server...",
        "please wait until server has fully started"))
    load_model_from_file()
    app.run(host='0.0.0.0', port=port)