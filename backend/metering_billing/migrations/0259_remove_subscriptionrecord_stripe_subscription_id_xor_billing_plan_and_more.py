# Generated by Django 4.0.5 on 2024-05-14 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metering_billing', '0258_alter_planversion_target_customers'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscriptionrecord',
            name='stripe_subscription_id_xor_billing_plan',
        ),
        migrations.AddConstraint(
            model_name='subscriptionrecord',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('stripe_subscription_id__isnull', False), models.Q(('stripe_subscription_id', ''), _negated=True), ('billing_plan__isnull', True)), models.Q(models.Q(('stripe_subscription_id__isnull', True), ('stripe_subscription_id', ''), _connector='OR'), ('billing_plan__isnull', False)), _connector='OR'), name='stripe_subscription_id_xor_billing_plan'),
        ),
    ]
