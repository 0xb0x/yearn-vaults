import brownie


def test_good_migration(
    token, strategy, vault, gov, strategist, guardian, TestStrategy, rando
):
    # Call this once to seed the strategy with debt
    strategy.harvest({"from": strategist})

    strategy_debt = vault.strategies(strategy)[4]  # totalDebt
    prior_position = token.balanceOf(strategy)
    assert strategy_debt > 0
    assert prior_position > 0

    new_strategy = strategist.deploy(TestStrategy, vault, gov)
    assert vault.strategies(new_strategy)[4] == 0
    assert token.balanceOf(new_strategy) == 0

    # Only Governance can migrate
    with brownie.reverts():
        vault.migrateStrategy(strategy, new_strategy, {"from": rando})
    with brownie.reverts():
        vault.migrateStrategy(strategy, new_strategy, {"from": strategist})
    with brownie.reverts():
        vault.migrateStrategy(strategy, new_strategy, {"from": guardian})

    vault.migrateStrategy(strategy, new_strategy, {"from": gov})
    assert vault.strategies(strategy)[4] == 0
    assert vault.strategies(new_strategy)[4] == strategy_debt
    assert token.balanceOf(new_strategy) == prior_position


def test_bad_migration(token, vault, strategy, gov, strategist, TestStrategy, Vault):
    different_vault = gov.deploy(Vault, token, gov, gov)
    new_strategy = strategist.deploy(TestStrategy, different_vault, gov)

    # Can't migrate to a strategy with a different vault
    with brownie.reverts():
        vault.migrateStrategy(strategy, new_strategy, {"from": gov})
