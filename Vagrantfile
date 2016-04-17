# Setup a CentOS 7 box and provision it with Ansible
# The server is configured with PostgreSQL 9.5 and Python
Vagrant.configure("2") do |config|
  config.vm.box = "bento/centos-7.1"
  config.vm.hostname = "cfpb.box"
  config.vm.network :forwarded_port, guest: 5006, host: 5006

  config.vm.provider :virtualbox do |vb|
    vb.customize [
      "modifyvm", :id,
      "--memory", "2048",
      "--cpus", "2"
    ]
  end

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "provision/provision.yml"
  end
end
