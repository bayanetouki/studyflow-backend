from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Team, TeamMembership, SharedTask, Message

User = get_user_model()


class MemberSerializer(serializers.ModelSerializer):
    """Afficher les membres d'une équipe."""
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'avatar']


class TeamMembershipSerializer(serializers.ModelSerializer):
    user = MemberSerializer(read_only=True)

    class Meta:
        model = TeamMembership
        fields = ['user', 'role', 'joined_at']


class TeamSerializer(serializers.ModelSerializer):
    owner = MemberSerializer(read_only=True)
    memberships = TeamMembershipSerializer(
        source='teammembership_set', many=True, read_only=True
    )
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'owner', 'invitation_code',
                  'memberships', 'members_count', 'created_at']
        read_only_fields = ['id', 'invitation_code', 'created_at']

    def get_members_count(self, obj):
        return obj.members.count()

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        team = super().create(validated_data)
        # Le créateur devient automatiquement membre (owner)
        TeamMembership.objects.create(team=team, user=team.owner, role='owner')
        return team


class SharedTaskSerializer(serializers.ModelSerializer):
    assigned_to = MemberSerializer(many=True, read_only=True)
    assigned_to_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source='assigned_to',
        required=False
    )
    created_by = MemberSerializer(read_only=True)

    class Meta:
        model = SharedTask
        fields = [
            'id', 'team', 'title', 'description', 'priority',
            'progress', 'due_date', 'completed',
            'assigned_to', 'assigned_to_ids', 'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    sender = MemberSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'team', 'sender', 'content', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class JoinTeamSerializer(serializers.Serializer):
    """Rejoindre une équipe via code d'invitation."""
    invitation_code = serializers.CharField(max_length=20)
