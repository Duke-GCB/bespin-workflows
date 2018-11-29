import json
from rest_framework import serializers
from django.contrib.auth.models import User
from data.models import Workflow, WorkflowVersion, VMStrategy, WorkflowConfiguration, JobFileStageGroup, VMStrategy, \
    ShareGroup, VMFlavor, Job
from bespin_api_v2.jobtemplate import JobTemplate


class AdminWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        resource_name = 'workflows'
        fields = '__all__'


class AdminWorkflowVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowVersion
        resource_name = 'workflowversions'
        fields = ['id', 'workflow', 'description', 'object_name', 'created', 'version', 'url', 'fields']


class WorkflowVersionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    tag = serializers.SerializerMethodField(required=False)

    def get_name(self, obj):
        return obj.workflow.name

    def get_tag(self, obj):
        return "{}/v{}".format(obj.workflow.tag, obj.version)

    class Meta:
        model = WorkflowVersion
        resource_name = 'workflow-versions'
        fields = ('id', 'workflow', 'name', 'description', 'object_name', 'created', 'url', 'version',
                  'methods_document', 'fields', 'tag')


class WorkflowConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowConfiguration
        resource_name = 'workflow-configuration'
        fields = '__all__'


class VMFlavorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VMFlavor
        resource_name = 'vm-flavors'
        fields = '__all__'


class VMStrategySerializer(serializers.ModelSerializer):
    vm_flavor = VMFlavorSerializer(read_only=True)
    class Meta:
        model = VMStrategy
        resource_name = 'vm-strategies'
        fields = '__all__'


class JobTemplateMinimalSerializer(serializers.Serializer):
    workflow_tag = serializers.CharField()
    name = serializers.CharField(required=False)
    fund_code = serializers.CharField(required=False)
    job_order = serializers.DictField(required=False)

    def create(self, validated_data):
        return JobTemplate(**validated_data)


class JobTemplateSerializer(serializers.Serializer):
    workflow_tag = serializers.CharField()
    name = serializers.CharField()
    fund_code = serializers.CharField()
    job_order = serializers.DictField()
    stage_group = serializers.PrimaryKeyRelatedField(queryset=JobFileStageGroup.objects.all())
    job_vm_strategy = serializers.PrimaryKeyRelatedField(
        queryset=VMStrategy.objects.all(), required=False)
    job = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

    def create(self, validated_data):
        return JobTemplate(**validated_data)


class ShareGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShareGroup
        resource_name = 'share-group'
        fields = '__all__'
