# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-26 15:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipient', '0013_entity structure to duns'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicparentduns',
            name='awardee_or_recipient_uniqu',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='historicparentduns',
            name='broker_historic_duns_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='historicparentduns',
            name='legal_business_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicparentduns',
            name='ultimate_parent_legal_enti',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicparentduns',
            name='ultimate_parent_unique_ide',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicparentduns',
            name='year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipientlookup',
            name='duns',
            field=models.TextField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='statedata',
            name='median_household_income',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=23, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='recipientprofile',
            unique_together=set([('recipient_hash', 'recipient_level')]),
        ),
        migrations.AddIndex(
            model_name='recipientprofile',
            index=models.Index(fields=['recipient_unique_id'], name='recipient_p_recipie_7039a5_idx'),
        ),
        # A couple of random, "like" indexes that never existed in the database.
        migrations.RunSQL(
            sql='drop index recipient_lookup_duns_ae948c75_like',
            reverse_sql='create index recipient_lookup_duns_ae948c75_like on recipient_lookup(duns text_pattern_ops)'
        ),
        migrations.RunSQL(
            sql='drop index duns_awardee_or_recipient_uniqu_81b7969d_like',
            reverse_sql='create index duns_awardee_or_recipient_uniqu_81b7969d_like on duns(awardee_or_recipient_uniqu text_pattern_ops)'
        ),
        # No idea why Django insists on creating this unique constraint.  PKs are unique by definition.
        migrations.RunSQL(
            sql="""
                alter table only historic_parent_duns
                    drop constraint if exists historic_parent_duns_broker_historic_duns_id_0dd7a627_uniq
            """,
            reverse_sql="""
                alter table only historic_parent_duns
                    add constraint historic_parent_duns_broker_historic_duns_id_0dd7a627_uniq unique (broker_historic_duns_id)
            """
        ),
        # Add some defaults in the database.
        migrations.RunSQL(
            sql='alter table only recipient_profile alter column last_12_months set default 0.00',
            reverse_sql='alter table only recipient_profile alter column last_12_months drop default'
        ),
        migrations.RunSQL(
            sql="alter table only recipient_profile alter column recipient_affiliations set default '{}'::text[]",
            reverse_sql='alter table only recipient_profile alter column recipient_affiliations drop default'
        ),
        # Add an index that we were unable to add using purely Django.  Django does not allow
        # inclusion of operation classes (gin_trgm_ops) in index creation until 2.2.
        migrations.RunSQL(
            sql='create index idx_recipient_profile_name on recipient_profile using gin (recipient_name gin_trgm_ops)',
            reverse_sql='drop index idx_recipient_profile_name'
        ),
    ]