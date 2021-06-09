from constants import *



nowTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
t = os.path.join(LOGS, 'logs - ' + nowTime)
network_dir = os.path.join(t, NETWORK)
clustering_dir = os.path.join(t, CLUSTERING)
models_dir = os.path.join(t, MODELS)
boot_dir = os.path.join(t, BOOT)



if not os.path.exists(LOGS):
    os.mkdir(LOGS)
    os.mkdir(t)
    os.mkdir(network_dir)
    os.mkdir(clustering_dir)
    os.mkdir(models_dir)
    os.mkdir(boot_dir)

else:
    shutil.rmtree(LOGS)
    os.mkdir(LOGS)
    os.mkdir(t)
    os.mkdir(network_dir)
    os.mkdir(clustering_dir)
    os.mkdir(models_dir)
    os.mkdir(boot_dir)

    print('logs folder created')

# ########### Create log files ##############

network_log = Create_logger('network_log' ,os.path.join(network_dir,'network.log'))
clustering_log = Create_logger('clustering_log', os.path.join(clustering_dir,'clustering.log'))
models_log = Create_logger('models_log', os.path.join(models_dir,'models.log'))
boot_log = Create_logger('boot_log', os.path.join(boot_dir,'boot.log'),logging.DEBUG)

# ----- Examples -----: TODO delete examples


#ip = '10.0.0.1'
#status =  ' connected'
#network_log.info(ip + status)
#
#
############ clustering ##############
#
#
#num_of_clusters = '4 '
#cluster1_size = '30 '
#cluster2_size = '30 '
#cluster3_size = '30 '
#cluster4_size = '30 '
#clustering_log.info(num_of_clusters  + cluster1_size + cluster2_size + cluster3_size + cluster4_size)
#
## ########### build rnn models ##############
#
#models_log.info('RNN created')
#
#
################### boot log ###################
#boot_log.debug('server is up')
#boot_log.debug('server is down!')
