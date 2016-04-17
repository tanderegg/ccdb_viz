# Setup a CentOS 7 box and provision it with Ansible
# The server is configured with PostgreSQL 9.5 and Python
Vagrant.configure("2") do |config|
  config.vm.box = "bento/centos-7.1"
  config.vm.hostname = "cfpb.box"
  config.vm.network :private_network, ip: "10.0.1.2"

  config.vm.provider :virtualbox do |vb|
    vb.customize [
      "modifyvm", :id,
      "--memory", "2048"
    ]
  end

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "provision/provision.yml"
  end
end
