#!/usr/bin/python
import autoscale_config
from subprocess import Popen, PIPE
import sys
import re
import boto
import boto.elasticache
#import boto.elasticache.layer1
import datetime
#from datetime import datetime
import smtplib
from email.mime.text import MIMEText

#Create elasticache connection
def connection_create():
    	conn = boto.elasticache.connect_to_region(autoscale_config.REGION,aws_access_key_id=autoscale_config.AWS_ACCESS_KEY,aws_secret_access_key=autoscale_config.AWS_SECRET_KEY)
	desc=conn.describe_cache_clusters(cache_cluster_id=autoscale_config.CLUSTER_ID, show_cache_node_info=1)
#	print desc
	return desc

def status_cluster(desc):
	status = desc['DescribeCacheClustersResponse']['DescribeCacheClustersResult']['CacheClusters'][0]['CacheClusterStatus']
#	print status
	return status

def find_maxsize(desc): 
        elasticache_endpoint = desc['DescribeCacheClustersResponse']['DescribeCacheClustersResult']['CacheClusters'][0]['ConfigurationEndpoint']
       	elasticache_address = elasticache_endpoint['Address']
	elasticache_port = elasticache_endpoint['Port']
	cmd="echo stats | nc  " + str(elasticache_address) + " " + str(elasticache_port) + "| grep limit_maxbytes  | awk '{print $3}' | tr -d '[:space:]'" 
	proc1 = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        max_size = proc1.communicate()[0]
#	print max_size
	return max_size

def number_of_nodes(desc):
	elasticache_numnodes = desc['DescribeCacheClustersResponse']['DescribeCacheClustersResult']['CacheClusters'][0]['NumCacheNodes']
#	print elasticache_numnodes
	return elasticache_numnodes



def find_node_freespace(desc,elasticache_numnodes):

	end_time = datetime.datetime.utcnow()
	start_time = end_time - datetime.timedelta(minutes=1)

	# This sets up the connection information to CloudWatch.  
	cloudwatch_connection = boto.connect_cloudwatch(autoscale_config.AWS_ACCESS_KEY,autoscale_config.AWS_SECRET_KEY)
	#metrics = cloudwatch_connection.list_metrics(metric_name='FreeableMemory')
	metrics = cloudwatch_connection.list_metrics(namespace="AWS/ElastiCache", dimensions={'CacheClusterId':'test','CacheNodeId':'0001'})
	statistics = ['Average', 'Minimum']
	unit='Bytes'
	metric_name='UnusedMemory'
	namespace="AWS/ElastiCache"
	elasticache_Nodeid = []
	free_space = []
	for i in range(0, elasticache_numnodes):
	    	Nodeid = desc['DescribeCacheClustersResponse']['DescribeCacheClustersResult']['CacheClusters'][0]['CacheNodes'][i]['CacheNodeId']
#		print Nodeid
		dimensions={'CacheClusterId':'test','CacheNodeId':Nodeid}
#		print dimensions
		freespace = cloudwatch_connection.get_metric_statistics(60, start_time, end_time, metric_name, namespace, statistics, dimensions, unit)
#		print freespace
#		print freespace[1]['Average']
		free_space.append(freespace[0]['Average'])
#		print free_space[i]
	return free_space

def find_node_remove(desc,elasticache_numnodes):
	for i in range(0, elasticache_numnodes):
                Nodeid = desc['DescribeCacheClustersResponse']['DescribeCacheClustersResult']['CacheClusters'][0]['CacheNodes'][i]['CacheNodeId']
	return Nodeid
	
def scale_up_check(free_space_list,maxsize):
	scale_up_required=0
	scale_down_required=0
	for freespace in free_space_list:
	  	pc=(float(freespace)/float(maxsize))*100
		print pc
		if pc < 20.0:
			scale_up_required=scale_up_required+1
	return scale_up_required


def scale_down_check(free_space_list,maxsize):
	scale_down_required=0
	for freespace in free_space_list:
	  	pc=(float(freespace)/float(maxsize))*100
		print pc
		if pc > 90:
			scale_down_required=scale_down_required+1
	return scale_down_required

def scale_up_cluster(elasticache_numnodes):
	 conn = boto.elasticache.connect_to_region(autoscale_config.REGION,aws_access_key_id=autoscale_config.AWS_ACCESS_KEY,aws_secret_access_key=autoscale_config.AWS_SECRET_KEY)
	 msg=conn.modify_cache_cluster(cache_cluster_id=autoscale_config.CLUSTER_ID, num_cache_nodes=elasticache_numnodes+1, apply_immediately=True)
	 return msg

def scale_down_cluster(elasticache_numnodes,node_to_remove):
         conn = boto.elasticache.connect_to_region(autoscale_config.REGION,aws_access_key_id=autoscale_config.AWS_ACCESS_KEY,aws_secret_access_key=autoscale_config.AWS_SECRET_KEY)
         msg=conn.modify_cache_cluster(cache_cluster_id=autoscale_config.CLUSTER_ID, num_cache_nodes=elasticache_numnodes-1, cache_node_ids_to_remove=[node_to_remove],apply_immediately=True)
         return msg

