#!/usr/bin/python
import autoscale_config
import autoscale_modules
#Main function
def main():
        try:
                desc=autoscale_modules.connection_create()
		status = autoscale_modules.status_cluster(desc) 
		if status != 'available':
			raise Exception("Cluster is not available. Current status : " + status )
		maxsize=autoscale_modules.find_maxsize(desc)
		elasticache_numnodes=autoscale_modules.number_of_nodes(desc)
		free_space_list=autoscale_modules.find_node_freespace(desc,elasticache_numnodes)
		scale_up_required=autoscale_modules.scale_up_check(free_space_list,maxsize)
		print 	scale_up_required	
		if scale_up_required == elasticache_numnodes:
			if autoscale_config.MAX_NODE > elasticache_numnodes:
				msg=autoscale_modules.scale_up_cluster(elasticache_numnodes)
			else:
				raise Exception("Cluster reached Max nodes, no further scale up possible..")

		else:
			scale_down_required=autoscale_modules.scale_down_check(free_space_list,maxsize)
			if scale_down_required == elasticache_numnodes:
				if autoscale_config.MIN_NODE < elasticache_numnodes:
					node_to_remove=autoscale_modules.find_node_remove(desc,elasticache_numnodes)
					msg=autoscale_modules.scale_down_cluster(elasticache_numnodes,node_to_remove)
					print msg
				else:
					raise Exception("Cluster reached MIN nodes, no futher scale down possible..")
	except Exception, e:
                print "Exception : "+str(e)
        return

if __name__ == '__main__':
        main()
