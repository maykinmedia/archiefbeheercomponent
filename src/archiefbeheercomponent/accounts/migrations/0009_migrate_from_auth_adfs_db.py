# Generated by Django 3.2.14 on 2022-07-27 14:35

import sys

from django.db import migrations

from django_auth_adfs.config import provider_config, settings as auth_adfs_settings
from mozilla_django_oidc_db.forms import OpenIDConnectConfigForm


def from_auth_adfs_to_mozilla_oidc(apps, schema_editor):
    # Patch a missing setting in newer versions of django-auth-adfs > 1.6.1
    auth_adfs_settings.VERSION = "v2.0"

    ADFSConfig = apps.get_model("django_auth_adfs_db", "ADFSConfig")
    OpenIDConnectConfig = apps.get_model(
        "mozilla_django_oidc_db", "OpenIDConnectConfig"
    )

    adfs_config = ADFSConfig.objects.first()
    if adfs_config is None:
        return

    oidc_config = OpenIDConnectConfig.objects.first()
    if oidc_config and oidc_config.oidc_op_discovery_endpoint:
        print("Existing OIDC config found, not overwriting it.", file=sys.stderr)
        return
    elif oidc_config is None:
        oidc_config = OpenIDConnectConfig()

    config_url = f"https://{auth_adfs_settings.SERVER}/{auth_adfs_settings.TENANT_ID}/"
    provider_config.load_config()

    # copy configuration over
    form = OpenIDConnectConfigForm(
        instance=oidc_config,
        data={
            "enabled": adfs_config.enabled,
            "oidc_rp_client_id": adfs_config.client_id,
            "oidc_rp_client_secret": adfs_config.client_secret,
            "oidc_rp_sign_algo": "RS256",
            "oidc_op_discovery_endpoint": config_url,
            "username_claim": adfs_config.username_claim,
            "claim_mapping": adfs_config.claim_mapping,
            "groups_claim": "roles",
            "sync_groups": adfs_config.sync_groups,
            "sync_groups_glob_pattern": "*",
        },
    )

    if not form.is_valid():
        print("Could not automatically migrate the ADFS config", file=sys.stderr)
        return

    form.save()
    adfs_config.enabled = False
    adfs_config.save()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_auto_20210215_1506"),
        ("django_auth_adfs_db", "0003_auto_20210323_1441"),
        ("mozilla_django_oidc_db", "0006_openidconnectconfig_unique_id_claim"),
    ]

    operations = [
        migrations.RunPython(from_auth_adfs_to_mozilla_oidc, migrations.RunPython.noop),
    ]
