/**
 * Charter Kit review-model card: the browser half of the DSH adapter.
 *
 * Hand-written closure-factory bundle in the DSH client-module convention.
 * It is committed as source (the repository's builders are pure Python and
 * must stay runnable without a Node toolchain), so keep it plain ES2020 and
 * require only modules from the shell's frozen platform table:
 * react, react/jsx-runtime, react-dom, react-dom/client, @deepseek-ai/cordis,
 * @deepseek-ai/dsh-client-store, @deepseek-ai/dsh-client-ui-slots,
 * @deepseek-ai/dsh-client-ui-primitives, @deepseek-ai/dsh-client-ui-dockkit.
 *
 * The card is keyed by the settings namespace the Host half registers, which
 * is what lets a plugin distributed outside the harness contribute a card.
 */
window.__ModuleLoader__.load({
  id: '@dsh-external/dsh-charter-kit',
  factory: (require) => {
    const module = { exports: {} }
    const exports = module.exports
    const React = require('react')
    const h = React.createElement

    const NS = 'charter-kit-review'
    const INHERIT = ''

    const zh = {
      title: 'Charter Kit 评审模型',
      description: '为 Review A / Review B 指定模型；未指定时跟随当前会话模型。',
      reviewA: 'Review A（契约与实现覆盖）',
      reviewB: 'Review B（对抗性评审）',
      inherit: '默认（跟随当前模型）',
      unavailable: '不可用',
      saving: '保存中…',
      saved: '已保存',
      failed: '保存失败',
      loadFailed: '模型目录加载失败',
      sameModel: 'A 与 B 使用同一模型；Review B 要求独立评审者，建议选不同模型。',
    }
    const en = {
      title: 'Charter Kit review models',
      description: 'Choose the model for Review A / Review B. Unset follows the current session model.',
      reviewA: 'Review A (contract and implementation coverage)',
      reviewB: 'Review B (adversarial review)',
      inherit: 'Default (follow current model)',
      unavailable: 'Unavailable',
      saving: 'Saving…',
      saved: 'Saved',
      failed: 'Save failed',
      loadFailed: 'Could not load the model catalog',
      sameModel: 'A and B share one model; Review B expects an independent reviewer — consider two models.',
    }

    /** @param route - provider/model route, or null for inherit. */
    function optionValue(route) {
      return route === null ? INHERIT : `${route.provider}\u0000${route.model}`
    }

    /** @param value - option value. */
    function parseOptionValue(value) {
      if (value === INHERIT) return null
      const at = value.indexOf('\u0000')
      if (at < 0) return null
      return { provider: value.slice(0, at), model: value.slice(at + 1) }
    }

    /** Read one stored route out of the settings value. */
    function storedRoute(value, providerField, modelField) {
      if (value[providerField] === '' || value[modelField] === '') return null
      return { provider: value[providerField], model: value[modelField] }
    }

    /**
     * Decide whether a queued write actually landed.
     *
     * `scope.mutate` RESOLVES when the Host refuses a write — the controller
     * recovers its mirror and returns — so resolution alone is not success. The
     * stored user layer is: an accepted write is folded back into it, while a
     * refused one leaves the previously stored value standing. This is the same
     * read-back the shell's own plugin cards perform (ui-settings-plugins'
     * card-form `store()`, which decides `failed` from `landed`).
     * @param scope - the bound namespace scope the write went through.
     * @param providerField - provider field the write addressed.
     * @param modelField - model field the write addressed.
     * @param provider - provider value the write intended.
     * @param model - model value the write intended.
     * @returns whether the user layer now holds both intended values.
     */
    function writeLanded(scope, providerField, modelField, provider, model) {
      const user = scope.getSnapshot().user
      if (user === null || typeof user !== 'object') return false
      return user[providerField] === provider && user[modelField] === model
    }

    function ReviewModelCard(props) {
      const { scope, loadCatalog, t } = props
      const [snapshot, setSnapshot] = React.useState(() => scope.getSnapshot())
      const [groups, setGroups] = React.useState(null)
      const [catalogFailed, setCatalogFailed] = React.useState(false)
      const [status, setStatus] = React.useState('')

      React.useEffect(() => scope.subscribe(() => { setSnapshot(scope.getSnapshot()) }), [scope])
      React.useEffect(() => {
        let live = true
        loadCatalog().then(
          (value) => { if (live) setGroups(value) },
          () => { if (live) setCatalogFailed(true) },
        )
        return () => { live = false }
      }, [loadCatalog])

      // A card renders nothing while its namespace is unavailable, matching
      // the shell's own cards: no trace beats a card nobody can act on.
      if (snapshot.status !== 'ready') return null

      const value = snapshot.value ?? {}
      const writable = snapshot.writable === true
      const routeA = storedRoute(value, 'reviewAProvider', 'reviewAModel')
      const routeB = storedRoute(value, 'reviewBProvider', 'reviewBModel')

      const options = [h('option', { key: '__inherit', value: INHERIT }, t('inherit'))]
      const seen = new Set([INHERIT])
      for (const group of groups ?? []) {
        for (const model of group.models) {
          const key = optionValue({ provider: group.id, model: model.id })
          seen.add(key)
          options.push(h('option', { key, value: key }, `${model.name} — ${group.name}`))
        }
      }
      // Each review gets its own choices. The catalogue portion is shared, but
      // a route the catalogue no longer serves is offered only under the review
      // that still stores it, so neither dropdown can be pointed at the other
      // review's route.
      const optionsFor = (route) => {
        if (route === null) return options
        const key = optionValue(route)
        if (seen.has(key)) return options
        return options.concat([
          h('option', { key, value: key }, `${route.provider}/${route.model} — ${t('unavailable')}`),
        ])
      }

      const write = (providerField, modelField, selected) => {
        const route = parseOptionValue(selected)
        const provider = route === null ? '' : route.provider
        const model = route === null ? '' : route.model
        setStatus(t('saving'))
        // The revision is deliberately NOT passed. The bound scope's controller
        // resolves it itself (`expectedRevision ?? pendingRevision ?? snapshot
        // revision`), and that `pendingRevision` is what lets two selections
        // inside one mirror round-trip both land. Pinning the revision this card
        // read makes the Host refuse the second write as a settings conflict,
        // which the controller then recovers from by reloading — so the card
        // reports a failed save for a write the user watches land.
        scope.mutate([
          { op: 'set', path: [providerField], value: provider },
          { op: 'set', path: [modelField], value: model },
        ]).then(
          // A settled write is not necessarily an accepted one: the Host is the
          // only authority on that, so read back what it actually stored.
          () => {
            setStatus(writeLanded(scope, providerField, modelField, provider, model) ? t('saved') : t('failed'))
          },
          () => { setStatus(t('failed')) },
        )
      }

      const select = (label, providerField, modelField, route) => h(
        'label',
        { className: 'ck-row' },
        h('span', { className: 'ck-label' }, label),
        h('select', {
          className: 'ck-select',
          value: optionValue(route),
          disabled: !writable,
          onChange: (event) => { write(providerField, modelField, event.target.value) },
        }, optionsFor(route)),
      )

      const sameModel = routeA !== null && routeB !== null
        && routeA.provider === routeB.provider && routeA.model === routeB.model

      return h(
        'li',
        { className: 'ck-card' },
        h('div', { className: 'ck-head' },
          h('span', { className: 'ck-title' }, t('title')),
          h('span', { className: 'ck-desc' }, t('description'))),
        h('div', { className: 'ck-body' },
          select(t('reviewA'), 'reviewAProvider', 'reviewAModel', routeA),
          select(t('reviewB'), 'reviewBProvider', 'reviewBModel', routeB),
          catalogFailed ? h('p', { className: 'ck-note' }, t('loadFailed')) : null,
          sameModel ? h('p', { className: 'ck-note' }, t('sameModel')) : null,
          status === '' ? null : h('p', { className: 'ck-status' }, status)),
      )
    }

    const STYLE = [
      '.ck-card{list-style:none;border:1px solid var(--dsw-alias-border-l2,#e5e5e5);border-radius:8px;padding:12px 14px;margin-bottom:8px}',
      '.ck-head{display:flex;flex-direction:column;gap:2px;margin-bottom:10px}',
      '.ck-title{font-size:14px;font-weight:600;color:var(--dsw-alias-label-primary,#111)}',
      '.ck-desc{font-size:12px;color:var(--dsw-alias-label-secondary,#666)}',
      '.ck-body{display:flex;flex-direction:column;gap:10px}',
      '.ck-row{display:flex;align-items:center;gap:10px}',
      '.ck-label{flex:0 0 210px;font-size:13px;color:var(--dsw-alias-label-primary,#111)}',
      '.ck-select{flex:1;min-width:0;padding:6px 8px;border-radius:6px;font-size:13px;'
        + 'border:1px solid var(--dsw-alias-border-l2,#ccc);background:var(--dsw-alias-bg-base,#fff);'
        + 'color:var(--dsw-alias-label-primary,#111)}',
      '.ck-note{margin:0;font-size:12px;color:var(--dsw-alias-label-secondary,#666)}',
      '.ck-status{margin:0;font-size:12px;color:var(--dsw-alias-label-secondary,#666)}',
    ].join('')

    exports.inject = ['slots', 'settingsScope', 'remote.session', 'locale']

    exports.apply = function apply(ctx) {
      ctx.effect(
        () => ctx.locale.register(NS, { zh, en }),
        'charter-kit: review card dictionaries',
      )
      const t = ctx.locale.bind(NS)
      const scope = ctx.settingsScope.bind({ namespace: NS })
      const styleId = `charter-kit-review-card`
      if (document.querySelector(`style[data-plugin-css="${styleId}"]`) === null) {
        const tag = document.createElement('style')
        tag.dataset.plugin = 'dsh-charter-kit'
        tag.dataset.pluginCss = styleId
        tag.textContent = STYLE
        document.head.appendChild(tag)
      }
      ctx.slots.inject('settings.plugin.item', () => ctx.slots.register({
        name: 'settings.plugin.item',
        key: NS,
        locale: NS,
        inject: () => ({
          scope,
          loadCatalog: () => ctx.remote.session.modelCatalog().then((response) => {
            if (!response.ok) throw new Error('model catalog unavailable')
            return response.value.groups
          }),
          t,
        }),
      }, ReviewModelCard))
    }

    return module.exports
  },
})
