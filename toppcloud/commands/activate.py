def command_activate(config):
    if not config.args.node:
        config.args.node = config.args.host
    config.run(
        ['ssh', 'www-mgr@%s' % config.node_hostname,
         '/var/www/support/activate-host.py %s %s' %
         (config.args.host, config.args.instance_name)])
    
