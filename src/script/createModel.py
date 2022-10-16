import turicreate as tc
import re

def createFrame():
    data = tc.image_analysis.load_images('src/data/', with_path=True)
    data['label'] = data['path'].apply(path2label)
    print(data)
    data.save('src/z-fighters.sframe')

def createModel():
    data =  tc.SFrame('src/z-fighters.sframe')
    data['label'] = data['path'].apply(path2label)
    data.save('src/z-fighters.sframe')
    model = tc.image_classifier.create(data, target='label')
    model.save('src/z-fighters.model')

def path2label(path):
    result = re.search('(?<=data/).*(?=/\d*.jpg)', path)
    if result != None:
        return result.group()

if __name__ == '__main__':
    createFrame()
    createModel()
    