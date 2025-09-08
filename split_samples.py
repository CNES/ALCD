#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path as op
from osgeo import ogr
import numpy as np
from random import shuffle


def get_random_splitting_lists(total_length, proportion):
    ''' Return two lists of random numbers, with the proportion
    defined.
    Derived from the number of features in the in_shp
    '''
    # Create a list of the range and shuffle it
    full_list = np.arange(0, total_length)
    np.random.shuffle(full_list)
    
    # Split the list in two
    cutoff = np.ceil(proportion*total_length)
    
    list1 = full_list[0:cutoff]
    list2 = full_list[cutoff:]
    
    return list1, list2
    
def shuffle_two_lists(list1, list2):
    ''' Shuffle two list in the same order
    Usefull for related lists
    e.g. :
    list1 = [1,2,3,4,5]
    list2 = [a,b,c,d,e]
    shuffle
    list1 = [1,3,5,4,2]
    list2 = [a,c,e,d,b]
    '''
    list1_shuf = []
    list2_shuf = []
    index_shuf = list(range(len(list1)))

    shuffle(index_shuf)
    for i in index_shuf:
        list1_shuf.append(list1[i])
        list2_shuf.append(list2[i])    
        
    return list1_shuf, list2_shuf
    
def split_points_sample(in_shp, train_shp, validation_shp, proportion, proportion_type = 'by_class'):
    ''' Split a shapefile's features into two shapefiles
    Used to split in a training and validation shapefiles
    Proportion (between 0 and 1) is the proportion for train_shp,
    and will be 1-proportion for validation_shp (generally proportion=0.7)
    '''
    # Get a Layer's Extent
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(in_shp, 0)
    inLayer = inDataSource.GetLayer()
    
    layerDefinition = inLayer.GetLayerDefn()
    srs = inLayer.GetSpatialRef()

    # get the field names
    field_names = []
    for i in range(layerDefinition.GetFieldCount()):
        field_names.append(layerDefinition.GetFieldDefn(i).GetName())
    
    shpDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    for dire in [train_shp, validation_shp]:
        if os.path.exists(dire):
            shpDriver.DeleteDataSource(dire)

    # Create the output shapefiles
    trainDataSource = shpDriver.CreateDataSource(train_shp)
    trainLayer = trainDataSource.CreateLayer("buff_layer", srs, geom_type=ogr.wkbPoint)
    
    validationDataSource = shpDriver.CreateDataSource(validation_shp)
    validationLayer = validationDataSource.CreateLayer("buff_layer", srs, geom_type=ogr.wkbPoint)


    # Add all the fields
    for field_name in field_names:
        newField = ogr.FieldDefn(field_name, ogr.OFTInteger)
        trainLayer.CreateField(newField)
        validationLayer.CreateField(newField)

    if proportion_type == 'by_class':
     # each class will respect the proportion
        points_classes_list = []
        points_FID_list = []
        
        # Get a list of all the classes and FID
        for point in inLayer:
            points_classes_list.append(point.GetField("class"))
            points_FID_list.append(point.GetFID())
            
        # Shuffle the two lists in the same order
        points_classes_list, points_FID_list = shuffle_two_lists(points_classes_list, points_FID_list)

        # Get the indexes to respect the quota
        train_idx = []
        validation_idx = []
        # for each class
        for class_name in list(set(points_classes_list)):
            # get all the indexes of the points belonging to that class
            class_indexes = [index for index, value in enumerate(points_classes_list) if value == class_name]
            shuffle(class_indexes) # added later, should really be random
            
            # set the max number of points with the command below
            cutoff = int(np.ceil(proportion*len(class_indexes)))
            # extend both lists 
            train_idx.extend(class_indexes[0:cutoff])
            validation_idx.extend(class_indexes[cutoff:])
        
        # Associate the indexes to the FIDs
        train_FID = [points_FID_list[idx] for idx in train_idx]
        validation_FID = [points_FID_list[idx] for idx in validation_idx]
        print(train_FID)
        print('{} training points will be taken'.format(len(train_FID)))
        print('{} validation points will be taken'.format(len(validation_FID)))
        
        inLayer.ResetReading() # needs to be reset to be readable again

        # Create the feature and set values
        for point in inLayer:
            current_FID = point.GetFID()
            if current_FID in train_FID:
                trainLayer.CreateFeature(point)
            elif current_FID in validation_FID:
                validationLayer.CreateFeature(point)    
            else:
                print('FID {} not in any list'.format(current_FID))

    elif proportion_type == 'global':
        # the proportion will be respected for the set of classes, i.e. 
        # a class can be not represented in the validation set 
        # Thus it is not recommended
        #Get the info of the shapefile
        global_proportion_type(inLayer, proportion, trainLayer, validationLayer)

    # Close DataSources
    inDataSource.Destroy()
    trainDataSource.Destroy()    
    validationDataSource.Destroy()    
    
    return


def global_proportion_type(inLayer, proportion, trainLayer, validationLayer):
    features_count = len(inLayer)
    train_list, validation_list = get_random_splitting_lists(features_count, proportion)
    print('{} training points will be taken'.format(len(train_list)))
    print('{} validation points will be taken'.format(len(validation_list)))
    # Create the feature and set values
    k = 0
    for point in inLayer:
        if k in train_list:
            trainLayer.CreateFeature(point)
        elif k in validation_list:
            validationLayer.CreateFeature(point)
        else:
            print('Feature {} not in any list'.format(k))
        k += 1


def k_split(in_shp, out_dir, K):
    '''
    Split the in_shp in K different sets
    They will be saved in the out_dir folder
    '''
    # Create the output dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print(out_dir + ' created')
    
    # Get a Layer's Extent
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(in_shp, 0)
    inLayer = inDataSource.GetLayer()
    
    layerDefinition = inLayer.GetLayerDefn()
    srs = inLayer.GetSpatialRef()

    # get the field names
    field_names = get_field_names(layerDefinition)

    shpDriver = ogr.GetDriverByName("ESRI Shapefile")

    # each class will respect the proportion
    points_classes_list = []
    points_FID_list = []
    
    # Get a list of all the classes and FID
    for point in inLayer:
        points_classes_list.append(point.GetField("class"))
        points_FID_list.append(point.GetFID())
        
    # Shuffle the two lists in the same order
    points_classes_list, points_FID_list = shuffle_two_lists(points_classes_list, points_FID_list)

    # Get the indexes to respect the quota
    train_idx = []
    validation_idx = []
    # for each class
    for class_name in list(set(points_classes_list)):
        # get all the indexes of the points belonging to that class
        class_indexes = [index for index, value in enumerate(points_classes_list) if value == class_name]
        shuffle(class_indexes)
        
        # split it into K chunks of same size
        K = int(K)
        splitted_class_indexes = np.array_split(class_indexes, K)
        
        # prepare all the k lists 
        for k in range(K):
            train_k_idx = np.concatenate([x for i,x in enumerate(splitted_class_indexes) if i!=k])
            validation_k_idx = np.concatenate([x for i,x in enumerate(splitted_class_indexes) if i==k])
            train_idx.append(train_k_idx)
            validation_idx.append(validation_k_idx)

    # here, train_idx and validation_idx contains K*nb_of_classes elements
    # it should be transformed into K elements by concatenating the list into
    # itself every nb_of_classes element
    nb_classes = len(list(set(points_classes_list)))
    
    train_idx_all_K = []
    validation_idx_all_K = []
    for k in range(K):
        train_idx_all_K.append(np.concatenate(train_idx[k::K]))
        validation_idx_all_K.append(np.concatenate(validation_idx[k::K]))

    for k in range(K):
        train_idx = train_idx_all_K[k]
        validation_idx = validation_idx_all_K[k]
        
        train_shp = op.join(out_dir, 'train_k_{}.shp'.format(k))
        validation_shp = op.join(out_dir, 'validation_k_{}.shp'.format(k))
                
        # Associate the indexes to the FIDs
        train_FID = [points_FID_list[int(idx)] for idx in train_idx]
        validation_FID = [points_FID_list[int(idx)] for idx in validation_idx]
        #~ print(train_FID)
        print('{} training points will be taken'.format(len(train_FID)))
        print('{} validation points will be taken'.format(len(validation_FID)))
        
        inLayer.ResetReading() # needs to be reset to be readable again

        # Remove output shapefile if it already exists
        for dire in [train_shp, validation_shp]:
            if os.path.exists(dire):
                shpDriver.DeleteDataSource(dire)

        # Create the output shapefiles
        trainDataSource = shpDriver.CreateDataSource(train_shp)
        trainLayer = trainDataSource.CreateLayer("buff_layer", srs, geom_type=ogr.wkbPoint)
        
        validationDataSource = shpDriver.CreateDataSource(validation_shp)
        validationLayer = validationDataSource.CreateLayer("buff_layer", srs, geom_type=ogr.wkbPoint)

        # Add all the fields
        add_all_fields(field_names, inLayer, trainLayer, train_FID, validationLayer, validation_FID)

        # Close DataSources
        trainDataSource.Destroy()    
        validationDataSource.Destroy()    

    inDataSource.Destroy()
    return


def get_field_names(layerDefinition):
    field_names = []
    for i in range(layerDefinition.GetFieldCount()):
        field_names.append(layerDefinition.GetFieldDefn(i).GetName())
    return field_names


def add_all_fields(field_names, inLayer, trainLayer, train_FID, validationLayer, validation_FID):
    for field_name in field_names:
        newField = ogr.FieldDefn(field_name, ogr.OFTInteger)
        trainLayer.CreateField(newField)
        validationLayer.CreateField(newField)

        # Create the feature and set values
        for point in inLayer:
            current_FID = point.GetFID()
            if current_FID in train_FID:
                trainLayer.CreateFeature(point)
            elif current_FID in validation_FID:
                validationLayer.CreateFeature(point)
            else:
                print('FID {} not in any list'.format(current_FID))
