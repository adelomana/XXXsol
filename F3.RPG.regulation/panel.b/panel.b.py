###
### this script creates a figure of FC and average expression for RNA-seq and Ribo-seq data sets
###

import sys,os,numpy
import matplotlib,matplotlib.pyplot

matplotlib.rcParams.update({'font.size':18,'font.family':'Arial','xtick.labelsize':14,'ytick.labelsize':14})
matplotlib.rcParams['pdf.fonttype']=42

def annotationReader():

    '''
    This function reads the annotation of microbes online and return a diccionary with GI identifiers to be used in DAVID 6.7 (these IDs are not recognized by DAVID 6.8).
    '''

    annotationMap={}

    with open(annotationFile,'r') as f:
        next(f)
        for line in f:
            v=line.split('\t')
            GI=v[2]
            sysName=v[7]
            annotationMap[sysName]=GI

    return annotationMap

def expressionReaderFC():

    '''
    This function creates a dictionary for expression values as:
    expression[comparison][trna/rbf][ribo-pt gene name]=foldchange
    '''

    expressionFC={}

    for timePoint in theTimePoints:
        comparison='tp.{}_vs_tp.1'.format(timePoint)
        expressionFC[comparison]={}
        
        for sampleType in sampleTypes:
            expressionDataFile=expressionDataDir+'significance.{}.condition_{}.csv'.format(sampleType,comparison)
            expressionFC[comparison][sampleType]={}

            with open(expressionDataFile,'r') as f:
                next(f)
                for line in f:
                    vector=line.split(',')

                    geneName=vector[0].replace('"','')
                    log2FC=float(vector[2])

                    if geneName in riboPtNames:
                        expressionFC[comparison][sampleType][geneName]=log2FC

    return expressionFC

def expressionReaderRC():

    '''
    this function creates a dictionary for expression values as
    expression[trna/rbf][ribo-pt gene name][timepoint][replicate]=value
    '''

    expressionRC={}
    
    geneNames=[]
    timepoints=[]
    replicates=[]

    for sampleType in sampleTypes:
        expressionDataFile=expressionDataDir+'normalizedCounts.{}.csv'.format(sampleType)

        with open(expressionDataFile,'r') as f:

            firstLine=f.readline()
            header=firstLine.split(',')
            sampleNames=header[1:]
            sampleNames[-1]=sampleNames[-1].replace('\n','')

            for line in f:
                vector=line.split(',')

                # geneName
                geneName=vector[0]
                if geneName in riboPtNames:

                    # gene Names
                    if geneName not in geneNames:
                        geneNames.append(geneName)

                    for i in range(len(vector)-1):
                    
                        # timepoint
                        timepoint='tp.{}'.format(int(sampleNames[i].split('.')[-1]))
                        if timepoint not in timepoints:
                            timepoints.append(timepoint)

                        # replicate
                        replicate='rep.{}'.format(int(sampleNames[i].split('rep.')[1][0]))
                        if replicate not in replicates:
                            replicates.append(replicate)

                        # value
                        value=float(vector[i+1])

                        # make sure keys exist
                        if sampleType not in expressionRC.keys():
                            expressionRC[sampleType]={}
                        if geneName not in expressionRC[sampleType].keys():
                            expressionRC[sampleType][geneName]={}
                        if timepoint not in expressionRC[sampleType][geneName].keys():
                            expressionRC[sampleType][geneName][timepoint]={}

                        expressionRC[sampleType][geneName][timepoint][replicate]=value

    # sort variables
    sampleTypes.sort()
    geneNames.sort()
    timepoints.sort()
    replicates.sort()

    return expressionRC,sampleTypes,timepoints,replicates

def grapher():

    '''
    This function builds the figure.
    '''
        
    medianRNA_groupA=[];  medianRNA_groupB=[]
    medianRibo_groupA=[]; medianRibo_groupB=[]
    log2FCrna_groupA=[];  log2FCrna_groupB=[]
    log2FCribo_groupA=[]; log2FCribo_groupB=[]

    f=open('ribo.groupings.csv','w')
    f.write('# group,geneName,foldChange,medianExpression\n')

    for geneName in riboPtNames:

        # compute median RNA
        x=numpy.mean([expressionRC['trna'][geneName][timepoints[-1]][replicate] for replicate in replicates])
        y=numpy.mean([expressionRC['trna'][geneName][timepoints[0]][replicate] for replicate in replicates])
        z=numpy.median([x,y])

        # compute median Ribo
        u=numpy.mean([expressionRC['rbf'][geneName][timepoints[-1]][replicate] for replicate in replicates])
        v=numpy.mean([expressionRC['rbf'][geneName][timepoints[0]][replicate] for replicate in replicates])
        t=numpy.median([u,v])

        # saving file with the two different groups
        if expressionFC['tp.4_vs_tp.1']['trna'][geneName] > -4:
            f.write('{},{},{},{}\n'.format('group A',geneName,expressionFC['tp.4_vs_tp.1']['trna'][geneName],z))

            medianRNA_groupA.append(z)
            medianRibo_groupA.append(t)
            log2FCrna_groupA.append(expressionFC['tp.4_vs_tp.1']['trna'][geneName])
            log2FCribo_groupA.append(expressionFC['tp.4_vs_tp.1']['rbf'][geneName])
        else:
            f.write('{},{},{},{}\n'.format('group B',geneName,expressionFC['tp.4_vs_tp.1']['trna'][geneName],z))

            medianRNA_groupB.append(z)
            medianRibo_groupB.append(t)
            log2FCrna_groupB.append(expressionFC['tp.4_vs_tp.1']['trna'][geneName])
            log2FCribo_groupB.append(expressionFC['tp.4_vs_tp.1']['rbf'][geneName])

    f.close()

    # making the figure
    theSize=8

    f, (ax1, ax2) = matplotlib.pyplot.subplots(1, 2, sharey=True)
    ax1.plot(medianRNA_groupA,log2FCrna_groupA,'s',alpha=0.5,mew=0,ms=theSize,color='black',label='RNA-seq a')
    ax1.plot(medianRNA_groupB,log2FCrna_groupB,'D',alpha=0.5,mew=0,ms=theSize,color='black',label='RNA-seq b')
    ax1.set_xlim([7,17])
    ax1.set_ylim([-6.5,0])
    ax1.set_xlabel('Median over time,')
    ax1.set_ylabel('log$_2$ FC')
    ax1.set_xticks([8,10,12,14,16])
    ax1.grid(alpha=0.5, ls=':')
    ax1.legend(framealpha=1,loc=1,ncol=1,fontsize=14)
    
    ax2.plot(medianRibo_groupA,log2FCribo_groupA,'s',alpha=0.5,mew=0,ms=theSize,color='red',label='Ribo-seq a')
    ax2.plot(medianRibo_groupB,log2FCribo_groupB,'D',alpha=0.5,mew=0,ms=theSize,color='red',label='Ribo-seq b')
    ax2.set_xlim([3.5,10.5])
    ax2.set_ylim([-6.5,0])
    ax2.set_xlabel('log$_2$(normalized counts)')
    ax2.set_xticks([4,6,8,10])
    ax2.grid(alpha=0.5, ls=':')
    ax2.legend(framealpha=1,loc=1,ncol=1,fontsize=14)
    
    figureName='figure.changes.pdf'
    f.tight_layout()
    f.savefig(figureName)
    f.clf()
    
    return None

def riboPtNamesReader():

    '''
    This function reads the ribosomal protein names.
    '''

    riboPtNames=[]
    riboPtMap={}
    with open(ribosomalProteinsFile,'r') as f:
        next(f)
        for line in f:
            vector=line.split('\t')
            riboPtNames.append(vector[0])
            riboPtMap[vector[0]]=vector[1]
            
    return riboPtNames,riboPtMap

### MAIN

# 0. user defined variables
ribosomalProteinsFile='/Volumes/omics4tb/alomana/projects/TLR/data/ribosomalGeneNames.txt'
expressionDataDir='/Volumes/omics4tb/alomana/projects/TLR/data/DESeq2/'
annotationFile='/Volumes/omics4tb/alomana/projects/TLR/data/microbesOnline/genome.annotation.txt'
theTimePoints=[2,3,4]
sampleTypes=['trna','rbf']

# 1. read the data
print('reading data...')
riboPtNames,riboPtMap=riboPtNamesReader()
expressionFC=expressionReaderFC()
expressionRC,sampleTypes,timepoints,replicates=expressionReaderRC()
annotationMap=annotationReader()

# 2. plot the data
print('plotting data...')
grapher()

print('... done.')
