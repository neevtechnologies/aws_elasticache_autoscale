aws_elasticache_autoscale
=========================

Introduction:

This is python script using boto to automatically scale up or down the number of nodes in an elastic cache cluster. It basically does the following :

 * Scales the cache nodes up or down  horizontally based on the aggregate memory usage across nodes

 * It will collect the memory usage of all nodes in the specified cluster and :
	Add an additional node if the memory usage is more than max threshold in all nodes.
	Deletes one node from cluster if the memory usage is less than minimum threshold in all nodes.

 * Consists of 3 files : 2 module files and one main function file
	Module files :  autoscale_config.py and autoscale_modules.py
	Main file : cache_autoscale.py

 * Accepts the AWS region name, ElastiCache clustername, max_nodes, min_nodes, access/secret keys and scale up/down thresholds as config     	parameters

 * Checks whether the cluster is in available status before running the script

 * Can configure the maximum nodes and minimum nodes in config file


How to set it up :

Save the script files in some location on your system and add the configuration values to the file autoscale_config.py. Then add a cron job to run the script cache_autoscale.py periodically.

The script will connect to the cache node to find its max size. If the system does not have access to the cache node, edit the main file and add the node size in bytes there.

Note: It is not recommended to enter the access and secret key of your main aws account. Create an IAM user that have access only to ElastiCache and add its credentials on the script.
